"""
Provides a layer over Postgres using pyscopg2 connection pooling. The
Database class maintains the connection pool and is thread-safe. The
DatabaseConnection uses a connection from the pool to do database operaions
and is not thread-safe.
"""
from collections import defaultdict
from contextlib import contextmanager
import logging
import psycopg2
import psycopg2.pool as pp
from time import perf_counter
from threading import Lock
from util.describer import Describer
from util.open_record import OpenRecord
from util.timer import Timer

MIN_CONNECTIONS = 2
MAX_CONNECTIONS = 20

class DatabaseError(Exception):
    """Wrapper exception for database errors."""
    def __init__(self, sql, params=[], root_ex=None):
        self.message = "'%s'" % sql
        if len(params):
            self.message += ": %s" % params
        if root_ex is not None:
            self.message += " due to %s" % root_ex

    def __str__(self):
        return self.message


class Database:
    """
    Provides a pool of connections to a database. Two layers of context
    management. First layer opens and closes the connection pool. Second layer
    borrows a connection (DatabaseConnection) that will be returned to the pool.

    Example:

        with Database(user, pwd, dbname) as db:
            with db.connection() as dbconn:
                # user the dbconn to query and update database
    """

    def __init__(self, user, password, database,
                 host="127.0.0.1",
                 port="5432",
                 min_conns=MIN_CONNECTIONS,
                 max_conns=MAX_CONNECTIONS):
        """
        Create Database with 'user' as user name with 'password', connecting
        to 'database' name running on 'host' and 'port'. Connection pool will
        maintain minimum of 'min_conns' (default 2) and maximum of 'max_conns'
        (default 20) connections.
        """
        self.__user = user
        self.__database = database
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = port
        self.__min_conns = min_conns
        self.__max_conns = max_conns
        self.__in_use = 0
        self.__max_in_use = 0
        self.__desc = {}
        self.__lock = Lock()
        self.__start_time = perf_counter()

    def __enter__(self):
        """ Start the connection pool. """
        self.__conn_pool = pp.ThreadedConnectionPool(
            self.__min_conns,
            self.__max_conns,
            user=self.__user,
            password=self.__password,
            host=self.__host,
            port=self.__port,
            database=self.__database)
        logging.info("Started pool with %d connections.", self.__min_conns)
        return self

    def __exit__(self, *args):
        """ Close the connection pool. """
        self.__conn_pool.closeall()
        logging.info("Closed pool.")

    @contextmanager
    def connection(self):
        """
        Produce a connection that will be yielded to the client and
        closed when the block exits.
        """
        conn = self.__conn_pool.getconn()
        with self.__lock:
            self.__in_use += 1
            self.__max_in_use = max(self.__max_in_use, self.__in_use)
        dbconn = DatabaseConnection(conn)
        try:
            yield dbconn
        finally:
            dbconn.close()
            with self.__lock:
                # Gather timers and add to the describers.
                for k, v in dbconn.get_timers().items():
                    self.__desc.setdefault(k, Describer(k))
                    for x in v:
                        self.__desc[k].add(x)
            # Return the connection.
            self.__conn_pool.putconn(dbconn.get_conn())
            self.__in_use -= 1

    def describe(self):
        """
        Latency descriptive statistics for each type of reqquest.
        """
        dss = []
        with self.__lock:
            for d in self.__desc.values():
                ds = d.describe()
                ds.rps = ds.n / (perf_counter() - self.__start_time)
                dss.append(ds)
        return dss

    def __str__(self):
        return "Database(user='%s',database=%s,in_use=%d,max_in_use=%d)" % \
           (self.__user,
            self.__database,
            self.__in_use,
            self.__max_in_use)


class DatabaseConnection:
    """
    Represents a connection borrowed from the pool.
    """

    def __init__(self, conn):
        """ Create a DatabaseConnection with 'conn' connecting to the database. """
        self.__conn = conn
        self.__cursor = conn.cursor()
        self.__timers = defaultdict(list)

    def close(self):
        """ Close database cursor. """
        self.__cursor.close()

    def callproc(self, procname, *params):
        """
        Call function or procedure named 'procname' with zero or more
        'params' and returns are results produced by the function or
        procedure.
        """
        try:
            logging.debug("callproc: %s(%s)", procname, params)
            with Timer() as tm:
                result = self.__cursor.callproc(procname, params)
            self.__timers[procname].append(tm.millis)
            return result
        except Exception as ex:
            raise DatabaseError(procname, params, ex)

    def commit(self):
        """
        Commit updates done on the connection or in the database using
        a function or procedure. Functions automatically commit but the
        invoking connection will not see the changes until it is committed
        if read-committed transaction isolation is being used (the default).
        """
        logging.debug("Commit")
        self.__conn.commit()

    def get_conn(self):
        """ Return underlying connection. """
        return self.__conn

    def get_timers(self):
        """ Latency timers. """
        return self.__timers

    def query(self, sql, *params):
        """
        Run query 'sql' with zero or more 'params' and return results as
        OpenRecords.
        """
        try:
            with Timer() as tm:
                records = []
                logging.debug("query: %s: %s", sql, params)
                self.__cursor.execute(sql, params)
                names = [x[0] for x in self.__cursor.description]
                for row in self.__cursor:
                    records.append(OpenRecord(zip(names, row)))
            self.__timers['query'].append(tm.millis)
            return records
        except Exception as ex:
            raise DatabaseError(sql, params, ex)

    def query_many(self, sql, *params):
        """
        Run query 'sql' with zero or more 'params', returning a sequence of
        records.
        """
        return self.query(sql, params)

    def query_one(self, sql, *params):
        """
        Run query 'sql' with zero or more 'params', returning a single record
        or None if no results. Raises DatabaseError if more than one
        record returned.
        """
        x = self.query(sql, params)
        if len(x) > 1:
            raise DatabaseError("Multiple records found with %s" % sql, params)
        if not len(x):
            return None
        return x[0]

    def rollback(self):
        """ Rollback any updates not yet committed. """
        self.__conn.rollback()

    def update(self, sql, *params):
        """
        Execute update 'sql' with optional 'params'. Return rows affected.
        """
        ct = 0
        try:
            logging.debug("update %s: %s", sql, params)
            with Timer() as tm:
                if isinstance(sql, str):
                    self.__cursor.execute(sql, params)
                    ct += self.__cursor.rowcount
                elif isinstance(sql, list):
                    for s in sql:
                        self.__cursor.execute(s)
                        ct += cursor.rowcount
                else:
                    raise DatabaseError("Invalid sql type '%s'" % type(sql))
            oper = sql.strip().partition(' ')[0]
            self.__timers[oper].append(tm.millis)
        except Exception as ex:
            self.__conn.rollback()
            dberr = DatabaseError(sql, params, ex)
            logging.warning("Rolled-back: %s", dberr)
            raise dberr
        return ct
