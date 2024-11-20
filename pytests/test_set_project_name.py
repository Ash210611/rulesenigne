#
# Run this Unit Test from the parent/project directory using this command:
#       python -B -m pytest pytests/test_set_project_name.py
#
# ===============================================================================

import inspect
import os

import pytest  # For tmpdir_factory

import un_re.global_shared_variables as G
from un_re.initialize_env_variables import set_project_name
from un_re.setup_logging import closeup_thread_logging
from un_re.setup_logging import setup_logging


# ===============================================================================
@pytest.fixture
def setup(tmpdir_factory):
    G.INPUT_SQL_DIR = 'None'
    G.TEMP_DIR = tmpdir_factory.mktemp("logs")
    G.LOG_FILENAME = os.path.join(G.TEMP_DIR, "junk.log")


# print ('LOG_FILENAME = {0}'.format (G.LOG_FILENAME))

# ===============================================================================
def test_set_project_name_good_1(setup):  # pylint: disable=redefined-outer-name

    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('         {0} Running...'.format(this_function_name))
    setup_logging(G.LOG_FILENAME)

    initial_input = 'CCW-D/ccb-develop1-pipeline'
    expected_output = 'CCW-D/ccb'

    os.environ["JOB_NAME"] = initial_input
    set_project_name()
    actual_output = G.PROJECT_NAME

    assert expected_output == actual_output

    # It will only report passed on the next line if the assertion passes
    print('         Found project_name {0}'.format(G.PROJECT_NAME))
    print('         Passed.')
    closeup_thread_logging(G.LOG_FILENAME)


# ===============================================================================
def test_set_project_name_good_2(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('         {0} Running...'.format(this_function_name))
    setup_logging(G.LOG_FILENAME)

    initial_input = 'CCW-D/ccb-WI00253184_CCB_REQ1201'
    expected_output = 'CCW-D/ccb'

    os.environ["JOB_NAME"] = initial_input
    set_project_name()

    assert expected_output == G.PROJECT_NAME

    # It will only report passed on the next line if the assertion passes
    print('         Found project_name {0}'.format(G.PROJECT_NAME))
    print('         Passed.')
    closeup_thread_logging(G.LOG_FILENAME)


# ===============================================================================
def test_set_project_name_good_3(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('         {0} Running...'.format(this_function_name))
    setup_logging(G.LOG_FILENAME)

    initial_input = 'hadoop-d/hcta_datalake/develop-pipeline'
    expected_output = 'hadoop-d/hcta_datalake'

    os.environ["JOB_NAME"] = initial_input
    set_project_name()

    assert expected_output == G.PROJECT_NAME

    # It will only report passed on the next line if the assertion passes
    print('         Found project_name {0}'.format(G.PROJECT_NAME))
    print('         Passed.')
    closeup_thread_logging(G.LOG_FILENAME)


# ===============================================================================
def test_set_project_name_good_4(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('         {0} Running...'.format(this_function_name))
    setup_logging(G.LOG_FILENAME)

    initial_input = 'hadoop-d/customer_360/feature-WI00165391_1_22'
    expected_output = 'hadoop-d/customer_360'

    os.environ["JOB_NAME"] = initial_input
    set_project_name()

    assert expected_output == G.PROJECT_NAME

    # It will only report passed on the next line if the assertion passes
    print('         Found project_name {0}'.format(G.PROJECT_NAME))
    print('         Passed.')
    closeup_thread_logging(G.LOG_FILENAME)
