# pylint: disable=R1732			# Don't require the with for Pools

# File: process_files.py
#
# ===============================================================================
from multiprocessing import Pool

import sys

import un_re.global_shared_variables as G

# from    un_re.check_file_size         	import check_file_size
from un_re.check_all_rules import check_all_rules
from un_re.get_td_antlr_findings import get_td_antlr_findings
from un_re.get_all_esp_antlr_findings import get_all_esp_antlr_findings
from un_re.get_all_hive_antlr_findings import get_all_hive_antlr_findings
from un_re.get_all_sql_statements import get_all_sql_statements
from un_re.get_all_db2_sql_statements import get_all_db2_sql_statements
from un_re.get_databricks_sql_statements import get_databricks_sql_statements
from un_re.get_redshift_statements import get_redshift_statements
from un_re.get_snowflake_sql_statements import get_snowflake_sql_statements
from un_re.indent import indent
from un_re.load_configuration_files import load_configuration_files
from un_re.ore_read_files import ore_read_files
from un_re.ore_extract_sql_statements import ore_extract_sql_statements
from un_re.ore_parse_sql_statements import ore_parse_sql_statements
from un_re.process_one_esp_file import process_one_esp_file
from un_re.process_one_sql_file import process_one_sql_file
from un_re.process_one_json_file import process_one_json_file
from un_re.refresh_sql_statement_objs import refresh_sql_statement_objs


# ===============================================================================
# Python documentation for multiprocessing module:
#       https://docs.python.org/2.7/library/multiprocessing.html
#
# Python tutorial on the multiprocessing module:
#       https://www.blog.pythonlibrary.org/2016/08/02/python-201-a-multiprocessing-tutorial/
#
# See this ref is subprocesses hang
#       https://stackoverflow.com/questions/15314189/python-multiprocessing-pool-hangs-at-join
#
# ===============================================================================
def check_input_file_sizes():
    indent('Checking input file sizes')

    for G.FILE_OBJ in G.INPUT_FILES:
        if G.RULES_ENGINE_TYPE in ('TERADATA_DDL', 'DATAOPS_TDV_DDL'):
            # For TERADATA_DDL, the filenames are relative to the
            # location of the XML file.
            G.INPUT_FILENAME = G.XML_DIR + '/' + G.FILE_OBJ.input_filename_rel
        else:
            G.INPUT_FILENAME = G.FILE_OBJ.input_filename

    # Check certain rules that apply to the whole input filename
    # check_file_size (G.INPUT_FILENAME) # Will exit if any file is too big for Python

    G.LOGGER.info('Good         : No input files are too big.')


# ===============================================================================
def get_sql_statements_in_parallel():
    """
    In General, single SQL statements can be parsed in parallel.

    Some languages support compound SQL statements, like functions,
    procedures, and packages.  A compount SQL statement can contain any
    number of single SQL statements inside it.

    When the Rules Engine supports languages with compound statements, those
    cannot be parsed in parallel, because of the recursive nature of doing
    that.
    """
    get_all_sql_statements()

    if G.PARALLEL_DEGREE == 1:
        for file_num in range(len(G.FILE_DICT)):
            process_one_sql_file(file_num)

    else:
        G.LOGGER.info('Setting up the parallel workers...')
        pool = Pool(processes=G.PARALLEL_DEGREE)

        pool.map(process_one_sql_file, range(len(G.FILE_DICT)))

        # Cleanup
        pool.close()
        pool.join()

        indent('All parallel workers have finished now.')

        # The SQL_STATEENT_OBJS will have to be refreshed
        # after parallel processing, because the memory
        # structures from the child processes are no longer
        # available
        refresh_sql_statement_objs()

    G.LOGGER.info('-' * 80)

    G.LOGGER.info('All SQL commands have been parsed now.')

    if G.RULES_ENGINE_TYPE == 'HIVE_DDL_RE':
        get_all_hive_antlr_findings()
    elif G.RULES_ENGINE_TYPE == 'REDSHIFT':
        get_redshift_statements()
    else:
        get_td_antlr_findings()


# ===============================================================================
def get_sql_statements():
    if G.RULES_ENGINE_TYPE in ('TERADATA_DDL', 'TERADATA_DML', 'HIVE_DDL_RE', 'PG_RE', 'REDSHIFT'):
        # These RE types can Parse the SQL statements in parallel.
        # We cannot parse statements in parallel for languages if we
        # support compound SQL statements.   We need to parse
        # compound statements twice, which cannot be done in parallel.

        get_sql_statements_in_parallel()

    elif G.RULES_ENGINE_TYPE == 'DATABRICKS':

        get_databricks_sql_statements()

    elif G.RULES_ENGINE_TYPE == 'DATA_MODEL':

        for file_num in range(len(G.FILE_DICT)):
            process_one_json_file(file_num)

    elif G.RULES_ENGINE_TYPE == 'ESP_RE':

        for file_num in range(len(G.FILE_DICT)):
            process_one_esp_file(file_num)

        G.LOGGER.info('-' * 80)
        G.LOGGER.info('All ESP files have been parsed now.')

        get_all_esp_antlr_findings()

    elif G.RULES_ENGINE_TYPE == 'DB2_RE':

        get_all_db2_sql_statements()

    elif G.RULES_ENGINE_TYPE == 'SNOWFLAKE':

        get_snowflake_sql_statements()

    elif G.RULES_ENGINE_TYPE == 'ORE':

        ore_read_files()
        ore_extract_sql_statements()
        ore_parse_sql_statements()


# ===============================================================================
def process_files():
    '''
    At this point, the list of input files is in the G.FILE_DICT list.

    For each_file in that list:
        process_one_sql_file
        That will extract the SQL statements from that 1 file
        into the G.SQL_STATEMENT_OBJS list.

        Parse the SQL statements from that 1 file in parallel.
        It is likely that most of them are comments.

    After all files and SQL statements are read and parsed, then
    check_all_rules
    '''
    # -----------------------------------------------------------------------
    # check_input_file_sizes ()

    load_configuration_files()

    get_sql_statements()

    check_all_rules()

    sys.stdout.flush()
