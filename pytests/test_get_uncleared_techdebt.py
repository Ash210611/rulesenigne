#
# Run this Unit Test from the parent/project directory using this command:
#       python -B -m pytest pytests/test_get_uncleared_techdebt.py
#
# ===============================================================================

import inspect
import os
import re
import subprocess
import sys

import pytest

import un_re.class_definitions as C
import un_re.global_shared_variables as G
# -------------------------------------------------------------------------------
from un_re.antlr_compile_grammar import antlr_compile_grammar
from un_re.authorize_UN_RE import authorize_UN_RE
from un_re.check_r216 import check_r216
from un_re.fprint import fprint
from un_re.get_all_sql_statements import get_all_sql_statements
from un_re.get_cfg_classwords import get_cfg_classwords
from un_re.get_rules import get_rules
from un_re.get_ruleset_severities import get_ruleset_severities
from un_re.get_td_antlr_findings import get_td_antlr_findings
from un_re.get_uncleared_techdebt import get_uncleared_techdebt
from un_re.initialize_env_variables import initialize_env_variables
from un_re.process_one_sql_file import process_one_sql_file
from un_re.read_the_list_of_input_files import read_the_list_of_input_files
from un_re.setup_logging import setup_logging

# -------------------------------------------------------------------------------
# Add Antlr to the PATH
# Must do this before importing modules that need Antlr

proc = subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE)
result = proc.stdout.read()
result = result.strip()
G.SCRIPT_DIR = result.decode('utf-8')

ADD_PATH_1 = '{0}/un_re'.format(G.SCRIPT_DIR)
ADD_PATH_2 = '{0}/un_re/Antlr'.format(G.SCRIPT_DIR)

sys.path.insert(0, ADD_PATH_2)
sys.path.insert(0, ADD_PATH_1)

print(f'               Running from directory {G.SCRIPT_DIR}')
print(f'sys.path   =   {sys.path}')

PYTHONPATH = os.environ.get('PYTHONPATH', 'UNKNOWN')
if PYTHONPATH == 'UNKNOWN':
    PYTHONPATH = f'{ADD_PATH_1}:{ADD_PATH_2}'
else:
    PYTHONPATH = f'{ADD_PATH_1}:{ADD_PATH_2}:{PYTHONPATH}'
os.environ['PYTHONPATH'] = PYTHONPATH
print(f"PYTHONPATH =   {os.environ.get('PYTHONPATH')}")


# ===============================================================================
@pytest.fixture
def setup(tmpdir_factory):
    print('Running setup...')

    G.RULES_ENGINE_TYPE = 'TERADATA_DDL'

    # Create a directory to hold temporary files
    G.TEMP_DIR = str(tmpdir_factory.mktemp('logs'))

    # -----------------------------------------------------------------------
    os.environ["BRANCH"] = 'Testing'
    os.environ["BUILD_NUMBER"] = '10101'
    os.environ["JOB_NAME"] = 'CCW-D/testing-Testing_pipeline'

    # -----------------------------------------------------------------------
    G.XML_DIR = G.TEMP_DIR + '/teradata'
    os.mkdir(G.XML_DIR)
    G.XML_FILENAME = G.XML_DIR + '/liquibase.xml'

    G.INPUT_FILENAME_REL = 'input.sql'

    with open(G.XML_FILENAME, 'w') as f:
        fprint(f, '<databaseChangeLog \n' + \
               'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \n' + \
               'xmlns="http://www.liquibase.org/xml/ns/dbchangelog" \n' + \
               'xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog \n' + \
               'http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.3.xsd">\n')

        fprint(f, '\n')
        fprint(f, '<include file="{0}" relativeToChangelogFile="true"/>\n'.format(
            G.INPUT_FILENAME_REL))

        fprint(f, '\n')
        fprint(f, '<changeSet author="Release" id="${project.version}"/> \n' + \
               '</databaseChangeLog>\n')

    # -----------------------------------------------------------------------
    G.FILE_NUM = 0
    G.FILE_DICT[G.FILE_NUM] = G.INPUT_FILENAME_REL

    G.INPUT_FILENAME = os.path.join(G.XML_DIR, G.FILE_DICT[G.FILE_NUM])

    G.INPUT_DIR = G.XML_DIR
    G.WORKSPACE = G.TEMP_DIR

    G.INI_FILENAME = os.path.join(G.TEMP_DIR, 'junk.ini')
    with open(G.INI_FILENAME, 'w') as f:
        fprint(f, '[UN_RE]')
        fprint(f, 'RULES_ENGINE_TYPE=TERADATA_DDL')
        fprint(f, 'INPUT_DIR={0}'.format(G.INI_FILENAME))
        fprint(f, 'LOAD_EVENT_RECORDS=FALSE')
        fprint(f, 'VERBOSE=1')

    G.RULES[G.RULE_ID] = C.Rule(G.RULE_ID, 'ERROR')

    G.POSTGRES_JSON_FILENAME = os.path.join(G.TEMP_DIR, "postgres.json")
    G.ERROR_FILENAME = os.path.join(G.TEMP_DIR, 'Rules_Engine.errors')
    G.WARNING_FILENAME = G.TEMP_DIR + "/Rules_Engine.warnings"
    G.ANTLR_FILENAME = os.path.join(G.TEMP_DIR, 'antlr.log')
    G.WARNING_FILENAME = G.TEMP_DIR + "/Rules_Engine.warnings"
    G.LOG_FILENAME = G.TEMP_DIR + "/junk.log"

    print('WORKSPACE             = {0}'.format(G.WORKSPACE))
    print('SCRIPT_DIR            = {0}'.format(G.SCRIPT_DIR))
    print('INPUT_DIR             = {0}'.format(G.INPUT_DIR))
    print('LOG_FILENAME          = {0}'.format(G.LOG_FILENAME))
    print('INPUT_FILENAME_REL    = {0}'.format(G.INPUT_FILENAME_REL))
    print('INPUT_FILENAME        = {0}'.format(G.INPUT_FILENAME))

    G.SQL_STATEMENT = \
        '-- Ruleset: Techdebt, UserStory: US1234567 \n' + \
        'CREATE MULTISET TABLE CCW_RPT_V2V_DEV.REQ_CLBRTN_MONTHLY_ACTNBL_HIST, \n' + \
        '	NO BEFORE JOURNAL, \n' + \
        '	NO AFTER JOURNAL, \n' + \
        '	CHECKSUM = DEFAULT, \n' + \
        '	DEFAULT MERGEBLOCKRATIO \n' + \
        '	( \n' + \
        '	REQ_ID INTEGER NOT NULL DEFAULT 0, \n' + \
        "	RUN_DT DATE FORMAT 'MM/DD/YYYY', \n" + \
        "	RPT_END_DT DATE FORMAT 'MM/DD/YYYY', \n" + \
        "	INDIV_ENTERPRISE_ID VARCHAR(40) CHARACTER SET LATIN NOT CASESPECIFIC, \n" + \
        "	MEMBR_NUM VARCHAR(15) CHARACTER SET LATIN NOT CASESPECIFIC DEFAULT ' ',	\n" + \
        "	RPT_PERIOD VARCHAR(4) CHARACTER SET LATIN NOT CASESPECIFIC DEFAULT ' ',	\n" + \
        "	PROV_ID VARCHAR(7) CHARACTER SET LATIN NOT CASESPECIFIC DEFAULT ' ' \n" + \
        '	) \n' + \
        'PRIMARY INDEX ( REQ_ID ,INDIV_ENTERPRISE_ID ,PROV_ID );'

    with open(G.INPUT_FILENAME, 'w') as f:
        fprint(f, G.SQL_STATEMENT)

    # -----------------------------------------------------------------------
    setup_logging(G.LOG_FILENAME)
    initialize_env_variables()
    authorize_UN_RE()
    antlr_compile_grammar('TD16')
    get_rules()
    get_ruleset_severities()
    get_cfg_classwords()
    get_uncleared_techdebt()

    # Add the uncleared techdebt record needed for this particular test:
    this_debt = C.UnclearedTechdebt(400, G.INPUT_FILENAME_REL)
    G.UNCLEARED_TECHDEBT.append(this_debt)

    read_the_list_of_input_files()
    get_all_sql_statements()
    process_one_sql_file(0)
    get_td_antlr_findings()

    return 'Succeeded'


# ===============================================================================
def test_check_uncleared_techdebt(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    check_r216()  # <= Run the rule function here

    # Check for expected output
    found_error_as_expected = False
    with open(G.LOG_FILENAME, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if re.search('Techdebt usage is disallowed as uncleared', line):
                print('=' * 80)
                print('Found indicator:')
                print('')
                print(line)
                found_error_as_expected = True
                print('=' * 80)
                break

    assert found_error_as_expected

    # If the assertion fails, We will not print the following messages
    print('Rule {0} found the error condition as expected.'.format(G.RULE_ID))
    print('        Passed.')
