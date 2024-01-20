import unittest
import datetime as dt
import logging
import os
import sys
from util.logging_utils import setup_root_logger
from util.pg_database import Database
from util.util_tools import get_source_info

DBNAME = 'scobrc'
DBUSER = 'scobrc'

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

CREATE_TABLE = """
DROP TABLE IF EXISTS data;
CREATE TABLE data (
    id int not null primary key,
    name varchar(30) not null,
    cd int not null,
    cf real not null,
    dt timestamp not null
);
"""

def setup_logging(level=logging.INFO):
    fn = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    fp = "log/%s.log" % ''.join([c for c in fn if c.isalnum() or c == '_'])
    if not os.path.exists('log'):
        os.mkdir('log')
    fmt = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    logging.basicConfig(filename=fp, format=fmt, level=level, force=True)

now = dt.datetime.now()
RECORDS = (
    dict(id=1, name='abc', cd=44, cf=2.37, dt=now),
    dict(id=2, name='123', cd=45, cf=3.41, dt=now)
)
class DatabaseTest(unittest.TestCase):

    def setUpClass():
        setup_logging(logging.DEBUG)

    def setUp(self):
        with Database(DBNAME, DBUSER) as db:
            with db.connection() as dbconn:
                dbconn.run(CREATE_TABLE)
                dbconn.insert('data', RECORDS[0])
                dbconn.insert('data', RECORDS[1])

    def test_check_insert(self):
        print("-- %s(%d): %s --" % get_source_info())
        with Database(DBNAME, DBUSER) as db:
            with db.connection() as dbconn:
                for i, rec in enumerate(dbconn.query("select * from data")):
                    for fn, fv in rec.items():
                        self.assertEqual(RECORDS[i][fn], fv)

    def test_func(self):
        print("-- %s(%d): %s --" % get_source_info())
        with Database(DBNAME, DBUSER, ) as db:
            with db.connection() as dbconn:
                dbconn.execute("drop function if exists addxy")
                dbconn.execute(CREATE_PROC)
                rec = dbconn.query_one('select addxy(2.32, 5.85)')
                self.assertAlmostEqual(8.17, rec['addxy'], .001)

    def test_query_one(self):
        print("-- %s(%d): %s --" % get_source_info())
        with Database(DBNAME, DBUSER) as db:
            with db.connection() as dbc:
                rec = dbc.query_one("select * from data where id=%s", 1)
                self.assertTrue(isinstance(rec, dict))
                self.assertEqual(5, len(rec))
                for fn, fv in rec.items():
                    self.assertEqual(RECORDS[0][fn], fv)

    def test_query_many(self):
        print("-- %s(%d): %s --" % get_source_info())
        with Database(DBNAME, DBUSER) as db:
            with db.connection() as dbc:
                for i, rec in enumerate(dbc.query_many("select * from data")):
                    for fn, fv in rec.items():
                        self.assertEqual(RECORDS[i][fn], fv)

    def test_update(self):
        print("-- %s(%d): %s --" % get_source_info())
        with Database(DBNAME, DBUSER) as db:
            with db.connection() as dbc:
                rec = dict(id=1, name='klf')
                dbc.update('data', rec, 'id')


if __name__ == '__main__':
    unittest.main()
