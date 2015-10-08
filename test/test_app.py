import psycopg2
import testing.postgresql
from nose.tools import eq_
from app import insert, increment

# Reference to testing.postgresql database instance
db = None

# Connection to the database used to set the database state before running each
# test
db_con = None

# Map of database connection parameters passed to the functions we're testing
db_conf = None


def setUp(self):
    """ Module level set-up called once before any tests in this file are
    executed.  Creates a temporary database and sets it up """
    global db, db_con, db_conf
    db = testing.postgresql.Postgresql()
    # Get a map of connection parameters for the database which can be passed
    # to the functions being tested so that they connect to the correct
    # database
    db_conf = db.dsn()
    # Create a connection which can be used by our test functions to set and
    # query the state of the database
    db_con = psycopg2.connect(**db_conf)
    # Commit changes immediately to the database
    db_con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    with db_con.cursor() as cur:
        # Create the initial database structure (roles, schemas, tables etc.)
        # basically anything that doesn't change
        cur.execute(slurp('./setup.sql'))


def tearDown(self):
    """ Called after all of the tests in this file have been executed to close
    the database connecton and destroy the temporary database """
    db_con.close()
    db.stop()


def test_insert_int():

    # Ensure the database is in a known state before calling the function we're
    # testing
    with db_con.cursor() as cur:
        cur.execute(slurp('./test/fixtures/state_empty.sql'))

    # Attempt to insert an integer
    insert(db_conf, 42)

    # Inspect the state of the database and make some assertions
    with db_con.cursor() as cur:

        # Check the rows in the table after insert has been called
        cur.execute("""SELECT * from public.numbers;""")
        rows = cur.fetchall()
        # Using the eq_ function from nose.tools allows us to assert that
        # complex types are equal. Here we are saying that we expect a single
        # row with a single value of 42
        eq_(rows, [(42,)])


def test_insert_float():

    # Ensure the database is in a known state before calling the function we're
    # testing
    with db_con.cursor() as cur:
        cur.execute(slurp('./test/fixtures/state_empty.sql'))

    # Attempt to insert a float (should be converted to an integer)
    insert(db_conf, 42.6)

    # Inspect the state of the database and make some assertions
    with db_con.cursor() as cur:

        # Check the rows in the table after insert has been called
        cur.execute("""SELECT * from public.numbers;""")
        rows = cur.fetchall()
        # Expect a single row with the value of 43 (our float is converted to
        # an integer)
        eq_(rows, [(43,)])


def test_increment():

    # Ensure the database is in a known state
    with db_con.cursor() as cur:
        cur.execute(slurp('./test/fixtures/state_1-5.sql'))

    # Call the function we're testing
    increment(db_conf, 1)

    # Inspect the state of the database and make some assertions
    with db_con.cursor() as cur:
        # Get all rows (be explict about the order to make comparison easier)
        cur.execute("""SELECT * from public.numbers order by num;""")
        rows = cur.fetchall()
        eq_(rows, [(2,), (3,), (4,), (5,), (6,)])


def slurp(path):
    """ Reads and returns the entire contents of a file """
    with open(path, 'r') as f:
        return f.read()
