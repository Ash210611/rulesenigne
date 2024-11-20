#
# Run this Unit Test from the parent/project directory using this command:
#       python -B -m pytest pytests/test_get_cfg_techdebt_exclusions.py
#
# ===============================================================================

import inspect
import os
from pathlib import Path

import pytest

import un_re.global_shared_variables as G
from un_re.authorize_UN_RE import authorize_UN_RE
from un_re.get_cfg_techdebt_exclusions import get_cfg_techdebt_exclusions
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

    authorize_UN_RE()

    return 'Setup succeeded'


# ===============================================================================
def test_get_cfg_techdebt_exclusions_1(setup):
    '''
    Check that we can setup things successfully.
    '''

    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    activation_date = None
    test_object_name = 'NO_SUCH_OBJECT_NAME'

    get_cfg_techdebt_exclusions(activation_date)

    # Check for expected output
    if test_object_name not in G.TECHDEBT_EXCLUSIONS:
        test_object_classified_as_expected = True
    else:
        test_object_classified_as_expected = False

    assert test_object_classified_as_expected

    # If the assertion fails,  we will not print the following messages.
    # If the assertion passes, we will     print the following messages.
    print('When Activation Date = {0}, TECHDEBT_EXCLUSIONS excludes {1}, as expected.'.format(
        activation_date,
        test_object_name))
    print('        Passed.')


# ===============================================================================
def test_get_cfg_techdebt_exclusions_2(setup):
    '''
    LOB_CD was activated on 20210412, so it should be findable on 20210420
    '''

    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    activation_date = None
    test_object_name = 'LOB_CD'
    get_cfg_techdebt_exclusions(activation_date)

    # Check for expected classification
    if test_object_name in G.TECHDEBT_EXCLUSIONS:
        test_object_classified_as_expected = True
    else:
        test_object_classified_as_expected = False

    assert test_object_classified_as_expected

    # If the assertion fails,  we will not print the following messages.
    # If the assertion passes, we will     print the following messages.
    print('When Activation Date = {0}, TECHDEBT_EXCLUSIONS includes {1}, as expected.'.format(
        activation_date,
        test_object_name))
    print('        Passed.')


# ===============================================================================
def test_get_cfg_techdebt_exclusions_3(setup):
    '''
    BP_YEAR will not activated till 20210517, so it should not be findable on 20210420
    '''

    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    activation_date = '20210420'
    test_object_name = 'LOB_CD'
    get_cfg_techdebt_exclusions(activation_date)

    # Check for expected classification
    if test_object_name in G.TECHDEBT_EXCLUSIONS:
        test_object_classified_as_expected = True
    else:
        test_object_classified_as_expected = False

    assert test_object_classified_as_expected

    # If the assertion fails,  we will not print the following messages.
    # If the assertion passes, we will     print the following messages.
    print('When Activation Date = {0}, TECHDEBT_EXCLUSIONS includes {1}, as expected.'.format(
        activation_date,
        test_object_name))
    print('        Passed.')


# ===============================================================================
def test_get_cfg_techdebt_exclusions_4(setup):
    '''
    BP_YEAR will not activated till 20210517, so it should not be findable on 20210420
    '''

    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    activation_date = '20210420'
    test_object_name = 'BP_YEAR'
    get_cfg_techdebt_exclusions(activation_date)

    # Check for expected classification
    if test_object_name not in G.TECHDEBT_EXCLUSIONS:
        test_object_classified_as_expected = True
    else:
        test_object_classified_as_expected = False

    assert test_object_classified_as_expected

    # If the assertion fails,  we will not print the following messages.
    # If the assertion passes, we will     print the following messages.
    print('When Activation Date = {0}, TECHDEBT_EXCLUSIONS excludes {1}, as expected.'.format(
        activation_date,
        test_object_name))
    print('        Passed.')
