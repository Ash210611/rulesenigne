import psycopg2  # type: ignore

import un_re.global_shared_variables as G

from un_re.indent import indent
from un_re.print_msg import print_msg


# ===============================================================================
def run_pg_statement(sql_statement):
    '''
    Run a single SQL statement in the PG database
    '''

    rows = []

    if G.PG_CONNECTION is None:
        try:
            G.PG_CONNECTION = psycopg2.connect(
                database=G.DMV_DATABASE,
                user=G.DMV_USERNAME,
                password=G.DMV_PASSWORD,  # That DB has no customer data
                host=G.DMV_SERVER,
                port="5432",
                connect_timeout=10)

        except psycopg2.OperationalError as error:
            print_msg('NOTICE: Failed to failed to connect to the DMV database.')
            indent(f'Error: {error}')

    if G.PG_CONNECTION is not None:
        # If it connected successfully, run the SQL
        try:
            cur = G.PG_CONNECTION.cursor()
            cur.execute(sql_statement)
            rows = cur.fetchall()

        # G.PG_CONNECTION.close ()
        # Now that we will reuse the connection,
        # we don't need to close it.

        except psycopg2.OperationalError as error:
            print_msg('NOTICE: Failed to run this statement')
            indent(sql_statement)
            indent(f'Error: {error}')

    return rows
