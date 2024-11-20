#
# Run this Unit Test from the parent/project directory using this command:
#       python -B -m pytest pytests/test_get_cfg_multiset_base_tables.py
#
# ===============================================================================

import inspect
import os
from pathlib import Path

import pytest

import un_re.global_shared_variables as G
from un_re.authorize_UN_RE import authorize_UN_RE
from un_re.get_cfg_multiset_base_tables import get_cfg_multiset_base_tables
from un_re.get_cfg_multiset_base_tables import get_multiset_base_tables_locally
from un_re.setup_logging import setup_logging


# ===============================================================================
@pytest.fixture
def setup(tmpdir_factory):
    print('Running setup...')

    G.SCRIPT_DIR = str(Path(os.path.dirname(__file__)).parent)

    G.TEMP_DIR = tmpdir_factory.mktemp("logs")
    G.LOG_FILENAME = os.path.join(G.TEMP_DIR, "junk.log")
    setup_logging(G.LOG_FILENAME)

    G.POSTGRES_JSON_FILENAME = os.path.join(G.TEMP_DIR, "postgres.json")
    G.ERROR_FILENAME = os.path.join(G.TEMP_DIR, 'Rules_Engine.errors')

    G.SHOULD_CHECK_RULE = ['r213']

    authorize_UN_RE()

    return 'Setup succeeded'


# ===============================================================================
def test_get_cfg_multiset_base_tables_1(setup):
    '''
    Check that we can read the list of multiset base tables from somewhere.
    '''

    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('Running: {0}...'.format(this_function_name))

    get_cfg_multiset_base_tables()

    # Check for expected output
    num = len(G.MULTISET_BASE_TABLES)

    assert num > 0

    # If the assertion fails,  we will not print the following messages.
    # If the assertion passes, we will     print the following messages.
    print('Good   : Found the list of {0} multiset base tables from somewhere, as expected.'.format(
        num))
    print('         Passed.')


# ===============================================================================
def test_get_cfg_multiset_base_tables_2(setup):
    '''
    Check that we can read the list of multiset base tables locally.
    '''

    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('Running: {0}...'.format(this_function_name))

    get_multiset_base_tables_locally()

    # Check for expected output
    num = len(G.MULTISET_BASE_TABLES)

    assert num > 0

    # If the assertion fails,  we will not print the following messages.
    # If the assertion passes, we will     print the following messages.
    print('Good   : Found the list of {0} multiset base tables locally, as expected.'.format(
        num))
    print('         Passed.')
