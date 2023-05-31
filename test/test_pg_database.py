import unittest
import inspect
from subprocess import Popen, PIPE
from util.pg_database import Database

DBNAME = 'test_db'
DBUSER = 'test_user'
DBPWD = 'test_pwd'

CREATE_PROC = """
create function addxy(x float, y float)
    returns float
    language plpgsql
AS $$
BEGIN
    RETURN x + y;
END;
$$;
"""

CREATE_SQL = f"""
drop database if exists {DBNAME};
drop user if exists {DBUSER};
create database {DBNAME};
create user test_user with encrypted password '{DBPWD}';
grant all privileges on database {DBNAME} to {DBUSER};
"""

def init_db():
    sql = CREATE_SQL
    proc = Popen('psql', stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
    out, err = proc.communicate(sql.encode('UTF-8'))
    if proc.returncode != 0:
        raise ValueError("psql %s failed with %s" % (sql, err))


class DatabaseTest(unittest.TestCase):

    def setUp(self):
        init_db()

    def test_create_insert(self):
        print('-- %s --' % inspect.stack()[0][3])
        with Database(DBUSER, DBPWD, DBNAME) as db:
            with db.connection() as dbconn:
                sql = "create table data (id int, field text)"
                dbconn.update("create table data (id int, field text)")
                dbconn.update("insert into data values (1, 'x')")
                dbconn.update("insert into data values (2, 'y')")
                dbconn.commit()
            with db.connection() as dbconn:
                recs = dbconn.query("select * from data")
                self.assertEqual(2, len(recs))
                self.assertEqual(2, len(recs[0]))
                self.assertEqual(2, len(recs[1]))
                self.assertEqual(1, recs[0].id)
                self.assertEqual(2, recs[1].id)
                self.assertEqual('x', recs[0].field)
                self.assertEqual('y', recs[1].field)

    def test_func(self):
        print('-- %s --' % inspect.stack()[0][3])
        with Database(DBUSER, DBPWD, DBNAME) as db:
            with db.connection() as dbconn:
                dbconn.update(CREATE_PROC)
                dbconn.commit();
                rec = dbconn.query_one('select addxy(2.32, 5.85)')
                self.assertAlmostEqual(8.17, rec.addxy, .001)


if __name__ == '__main__':
    unittest.main()
