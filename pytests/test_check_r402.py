#
# Run this Unit Test from the parent/project directory using this command:
#       python -B -m pytest pytests/test_check_r402.py
#
# ===============================================================================

import inspect
import os

import pytest

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.check_r402 import check_r402
from un_re.setup_logging import setup_logging


# ===============================================================================
@pytest.fixture
def setup(tmpdir_factory):
    print('Running setup...')
    G.RULES_ENGINE_TYPE = 'TERADATA_DDL'

    G.RULE_ID = 'r402'
    G.SHOULD_CHECK_RULE[G.RULE_ID] = True
    G.RULES[G.RULE_ID] = C.Rule(G.RULE_ID, 'ERROR')

    G.INPUT_DIR = 'None'
    G.TEMP_DIR = tmpdir_factory.mktemp("logs")
    G.LOG_FILENAME = os.path.join(G.TEMP_DIR, "junk.log")
    # print ('LOG_FILENAME = {0}'.format (G.LOG_FILENAME))
    setup_logging(G.LOG_FILENAME)

    G.POSTGRES_JSON_FILENAME = os.path.join(G.TEMP_DIR, "postgres.json")
    G.ERROR_FILENAME = os.path.join(G.TEMP_DIR, 'Rules_Engine.errors')
    G.INPUT_FILENAME = os.path.join(G.TEMP_DIR, 'input.sql')
    G.ANTLR_FILENAME = os.path.join(G.TEMP_DIR, 'antlr.log')

    G.INPUT_FILE = C.InputFile(
        input_filename=r'/abs_path/somedir/check_r403.2.sql',
        input_filename_rel=r'somedir/check_r403.2.sql',
        filenum=0)
    # print (G.FILE_OBJ)
    G.INPUT_FILES.append(G.INPUT_FILE)

    G.DATABASE_BASE = 'CCW_BASE'
    G.SQL_STMT_NUM = 0
    G.COMMAND_TYPE = 'CREATE TABLE'
    G.SQL_STATEMENT = '		\
		Create Table check_r402_3	\
	        ,FALLBACK			\
	        ,NO BEFORE JOURNAL		\
	        ,NO AFTER JOURNAL		\
	        ,CHECKSUM = DEFAULT		\
	        ,DEFAULT MERGEBLOCKRATIO	\
	        ,MAP = TD_MAP2			\
	        (				\
		        C_ID_1 integer,		\
		        C_ID_2 integer,		\
		        C_ID_3 integer)		\
		NO primary index;'

    G.SQL_STATEMENT_OBJ = C.SQLStatementObj(
        G.SQL_STMT_NUM,
        G.SQL_STATEMENT,
        G.COMMAND_TYPE,
        G.INPUT_FILE.input_filename,
        G.INPUT_FILE.input_filename_rel,
        G.ANTLR_LOG_FILENAME,
        G.INPUT_FILE)

    G.TABLE_STRUCTURE = C.TableStructure(
        'CCW_BASE',
        'check_r402_3',
        G.SQL_STATEMENT_OBJ)

    G.TABLE_STRUCTURE.sql_stmt_num = G.SQL_STMT_NUM
    G.TABLE_STRUCTURE.sql_statement = G.SQL_STATEMENT

    G.TABLE_STRUCTURE.regulated_options.append('NO PRIMARY INDEX')

    G.TABLE_STRUCTURE.input_filename = G.INPUT_FILE.input_filename

    G.TABLE_STRUCTURES.append(G.TABLE_STRUCTURE)

    return 'Succeeded'


# ===============================================================================
def test_check_r402_no_primary_index_found(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    check_r402()  # <= Run the rule function here

    # Check for expected output
    found_error_as_expected = False
    with open(G.ERROR_FILENAME, 'r') as f:
        print('=' * 80)
        print('Error file contents:')
        print('')
        for line in f.readlines():
            line = line.strip()
            print(line)
            found_error_as_expected = True
        print('=' * 80)

    assert found_error_as_expected

    # If the assertion fails, We will not print the following messages
    print('Rule {0} found the error condition as expected.'.format(G.RULE_ID))
    print('        Passed.')
