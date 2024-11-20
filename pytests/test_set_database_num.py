#
# Run this Unit Test from the parent/project directory using this command:
#       python -B -m pytest pytests/test_set_database_num.py
#
# The list of known databases is read from a certain file, and stored in
# memory in the A.KNOWN_DB array.
#
# Every database script must specify at least 1 database reference.   To check
# if the referenced database is valid, the rules engine does a lookup from 
# the list of known databases.
#
# ===============================================================================

import inspect
import os
from pathlib import Path

import pytest

import un_re.KNOWN_DB as A
import un_re.global_shared_variables as G
from un_re.authorize_UN_RE import authorize_UN_RE
from un_re.get_cfg_known_db import get_cfg_known_db
from un_re.set_database_num import set_database_num
from un_re.setup_main_environment import setup_main_environment


# ===============================================================================
@pytest.fixture
def setup(tmpdir_factory):
    G.RULES_ENGINE_TYPE = 'TERADATA_DDL'
    G.VERBOSE = True
    G.DATABASE_NUM = -1

    G.SCRIPT_DIR = str(Path(os.path.dirname(__file__)).parent)

    G.TEMP_DIR = str(tmpdir_factory.mktemp("logs"))
    os.environ['WORKSPACE'] = G.TEMP_DIR

    setup_main_environment()
    authorize_UN_RE()

    print(f'G.DMV_PASSWORD={G.DMV_PASSWORD}')

    A.KNOWN_DB = []
    get_cfg_known_db()
    print(A.KNOWN_DB)
    print('\n')
    print(f'DMV_SERVER   = {G.DMV_SERVER}')
    print(f'DMV_DATABASE = {G.DMV_DATABASE}')
    print(f'DMV_USERNAME = {G.DMV_USERNAME}')
    print(f'DMV_PASSWORD = {G.DMV_PASSWORD}')


# ===============================================================================
def test_database_num_is_found(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))
    # print (A.KNOWN_DB)

    G.DATABASE_BASE = 'CCW_BASE'

    set_database_num()

    assert G.DATABASE_NUM >= 0
    print('        Passed.')


# ===============================================================================
def test_database_num_is_not_found(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))
    # print (A.KNOWN_DB)

    G.DATABASE_BASE = 'UNKNOWN'  # Or missing, or garbage

    set_database_num()

    assert G.DATABASE_NUM == -1
    print('        Passed.')
