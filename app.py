import psycopg2


def insert(db_conf, n):
    """ Inserts a number into the public.numbers table """
    sql = """INSERT INTO public.numbers VALUES (%(n)s)"""
    with psycopg2.connect(**db_conf) as con:
        with con.cursor() as cur:
            cur.execute(sql, {'n': n})


def increment(db_conf, n):
    """ Increments all numbers by n """
    sql = """UPDATE public.numbers SET num = num + (%(n)s)"""
    with psycopg2.connect(**db_conf) as con:
        with con.cursor() as cur:
            cur.execute(sql, {'n': n})
