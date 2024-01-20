""" Context-aware datasbase client using pyscopg2 connection pooling. """
from contextlib import contextmanager
import logging
import psycopg2.pool as pp

MIN_CONNECTIONS = 2
MAX_CONNECTIONS = 20


class DatabaseError(Exception):
    """Wrapper exception for database errors."""

    def __init__(self, sql, params=[], msg=None):
        self.message = "'%s'" % sql
        if len(params):
            self.message += ": %s" % params
        if msg is not None:
            self.message += " due to %s" % msg

    def __str__(self):
        return self.message


class Database:
    """
    Context-aware datasbase client using pyscopg2 connection pooling. The
    Database class maintains the connection pool and is thread-safe. The
    DatabaseConnection uses a connection from the pool and is not thread-safe.
    Any updates will be made in a single transaction committed when the
    connection is returned to the pool.

    Example:

    with Database(DBNAME, DBUSER) as db:
        with db.connection() as conn:
            # use conn
        # Commit any updates.
    """

    def __init__(self, dbname, user,
                 password=None,
                 host="127.0.0.1",
                 port="5432",
                 min_conns=MIN_CONNECTIONS,
                 max_conns=MAX_CONNECTIONS):
        """
        Create Database with 'user' as user name with 'password', connecting
        to 'dbname' name running on 'host' and 'port'. Connection pool will
        maintain minimum of 'min_conns' (default 2) and maximum of 'max_conns'
        (default 20) connections.
        """
        self.__user = user
        self.__dbname = dbname
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = port
        self.__min_conns = min_conns
        self.__max_conns = max_conns

    def __enter__(self):
        """ Start the connection pool. """
        self.__conn_pool = pp.ThreadedConnectionPool(
            self.__min_conns,
            self.__max_conns,
            user=self.__user,
            password=self.__password,
            host=self.__host,
            port=self.__port,
            dbname=self.__dbname)
        logging.info("Started pool with %d connections.", self.__min_conns)
        return self

    def __exit__(self, *args):
        """ Close the connection pool. """
        self.__conn_pool.closeall()
        logging.info("Closed pool.")

    @contextmanager
    def connection(self):
        """
        Produce a connection that will be yielded to the client and closed
        when the block exits.
        """
        conn = self.__conn_pool.getconn()
        dbconn = DatabaseConnection(conn)
        try:
            logging.info("Yield connection %s", id(dbconn))
            yield dbconn
        finally:
            logging.info("Release connection %s", id(dbconn))
            self.__conn_pool.putconn(dbconn.release())


class DatabaseConnection:
    """ A connection borrowed from the pool. """

    def __init__(self, conn):
        """ Create a DatabaseConnection with 'conn' connected to the database. """
        self.__conn = conn
        self.__cursor = conn.cursor()

    def callproc(self, procname, *params):
        """
        Call function or procedure named 'procname' with zero or more
        'params' and returns are results produced by the function or
        procedure.
        """
        try:
            logging.debug("%s: callproc: %s(%s)",
                          id(self.__conn), procname, params)
            return self.__cursor.callproc(procname, params)
        except Exception as ex:
            raise DatabaseError(procname, params) from ex

    def execute(self, sql, *params):
        """ Execute 'sql' with optional 'params'. Return rows affected. """
        ct = 0
        try:
            logging.debug("%s: update %s: %s", id(self.__conn), sql, params)
            self.__cursor.execute(sql, params)
            return self.__cursor.rowcount
        except Exception as ex:
            self.__conn.rollback()
            raise DatabaseError(sql, params) from ex
        return ct

    def insert(self, tbl, rec):
        """
        Insert dictionary record 'rec', where keys are column names,
        into table 'tbl'.
        """
        sql = f"INSERT INTO {tbl} ("
        sql += ','.join([fn for fn in rec])
        sql += ") VALUES ("
        sql += ','.join(['%s' for _ in rec])
        sql += ")"
        return self.execute(sql, *list(rec.values()))

    def query(self, sql, *params):
        """ Run query 'sql' with zero or more 'params', generating records. """
        try:
            logging.debug("%s: query: %s: %s", id(self.__conn), sql, params)
            self.__cursor.execute(sql, params)
            names = [x[0] for x in self.__cursor.description]
            for row in self.__cursor:
                yield dict(zip(names, row))
        except Exception as ex:
            raise DatabaseError(sql, params) from ex

    def query_many(self, sql, *params):
        """
        Run query 'sql' with zero or more 'params', where each param needs
        placeholder '%s' in 'sql', returning zero to many records.
        """
        return list(self.query(sql, params))

    def query_one(self, sql, *params):
        """
        Run query 'sql' with zero or more 'params', returning a single record
        or None if no results. Raises DatabaseError if more than one
        record returned.
        """
        x = list(self.query(sql, params))
        if len(x) > 1:
            raise DatabaseError(sql, params, "Expected only one record.")
        if not len(x):
            return None
        return x[0]

    def release(self):
        """
        Release this connection, committing any open transactions and
        closing the cursor, returning the connection.
        """
        self.__conn.commit()
        self.__cursor.close()
        self.__cursor = None
        return self.__conn

    def run(self, script):
        """ Run 'script', which can have multiple statements separate by ';'. """
        logging.debug("%s: run %s", id(self.__conn), script)
        while len(script):
            sql, _, script = script.partition(';')
            if len(sql.strip()):
                self.execute(sql.strip())

    def update(self, tbl, rec, keyfields):
        """
        Update table 'tbl' with dictionary record 'rec' with keys that
        match column names. 'keyfields' is a list of fields to consider as
        keys, simple equivalenced used in the where clause.
        """
        sql = f"UPDATE {tbl} SET "
        sql += ','.join([f"{fn}=%s" for fn in rec if fn not in keyfields])
        sql += " WHERE "
        sql += ' AND '.join([f"{fn}=%s" for fn in rec if fn in keyfields])
        params = [fv for fn, fv in rec.items() if fn not in keyfields]
        params += [fv for fn, fv in rec.items() if fn in keyfields]
        return self.execute(sql, *params)
