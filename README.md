# Testing Python Postgres Demo

A demonstration of writing unit tests for Python functions that perform some action on a Postgres database using testing.postgresql package and nose.

## Background

In an ideal world all functions would be pure and free of side-effects, however in the real world we often need to write functions who's job it is to create side-effects such as writing to a file or updating a database. There are case when mocks can be used to test such functions but often you need to test against an actual database inorder to test properties such as:

* the effects of triggers
* conversion of values to conform with a columns type
* ensuring constraints are enforced etc.

## Approach

This project demonstrates testing two very simple functions `insert` and `increment` which operate on a table `public.numbers`. The functions to test are defined in `app.py`, tests in `test/test_app.py` and resources used by the tests in `test/fixtures`.

The general approach is:

### Organisation

* Try and isolate the functionality that interacts with the database to individual functions, this will hopefully make other functions easier to test as they don't mess with the database and allow those functions that do to be tested in a consistent manner
* Pass either an existing database connection or the configuration needed to create a connection to the function so that they can be called independently. Both `insert` and `increment` accept a map of configuration parameters which make it possible to call them independently

### Writing tests

* Use module level set-up to create a fresh temporary database instance using testing.postgresql and use SQL script to setup the structure of the database (roles, schemas, tables, view, functions, triggers etc.) and load any data that does not change. Ideally this would be done before each test but as creating the temporary database take a second or two I've found it's generally OK to do the basic setup once and then reuse the database for all tests
* Have each individual test set the initial state of the database before calling the function to be tested, this is generally done by executing a SQL script such as `test/fixtures/state_1-5.sql` which first truncates the `public.numbers` table then inserts a known set of data
* Once the test has established the database state it can call the function to be tested followed by querying the database state in-order to determine if the function call and any associated database triggers, constraints etc. had the desired affect.

### Tips

#### Connecting to the temporary database

While writing tests and implementing functionality it's often useful to connect to the temporary database in-order to inspect it's current state. A simple way to pause the execution of the tests or the application being tested is to drop into the Python debugger `dpb` by inserting the following at the point in the code that you'd like to pause:

    import pdb; pdb.set_trace()

Once execution is paused you can get the connection parameters and connect to the database using `psql` by calling the following from within the debugger:

    db.url()

Then connect to the database using psql using the database connection URL `db.url()` returned:

    postgresql://postgres@127.0.0.1:46183/test

## Running

In order to run the project yourself, clone or download the repository then create a virtual environment and install dependencies with:

    pip install -r requirements.txt

then run the tests with (`--nocapture` avoids capturing stdout so you can see any print statements should a test fail; `--stop` stop running tests after the first error or failure):

    nosetests --nocapture --stop
