#
# Run this Unit Test from the parent/project directory using this command:
#       python -B -m pytest pytests/test_authorize_UN_RE.py
#

import inspect
import os
import subprocess
import sys

import pytest

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.authorize_UN_RE import authorize_UN_RE
from un_re.run_pg_statement import run_pg_statement
from un_re.setup_logging import setup_logging

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


# ===============================================================================
@pytest.fixture
def setup(tmpdir_factory):
    print('Running setup...')

    # Create a directory to hold temporary files
    G.TEMP_DIR = str(tmpdir_factory.mktemp('logs'))

    # -----------------------------------------------------------------------
    G.WORKSPACE = G.TEMP_DIR

    G.RULES[G.RULE_ID] = C.Rule(G.RULE_ID, 'ERROR')

    G.ERROR_FILENAME = os.path.join(G.TEMP_DIR, 'Rules_Engine.errors')
    G.WARNING_FILENAME = G.TEMP_DIR + "/Rules_Engine.warnings"
    G.WARNING_FILENAME = G.TEMP_DIR + "/Rules_Engine.warnings"
    G.LOG_FILENAME = G.TEMP_DIR + "/junk.log"

    print('WORKSPACE             = {0}'.format(G.WORKSPACE))
    print('SCRIPT_DIR            = {0}'.format(G.SCRIPT_DIR))
    print('LOG_FILENAME          = {0}'.format(G.LOG_FILENAME))

    # -----------------------------------------------------------------------
    if G.LOGGER is None:
        setup_logging(G.LOG_FILENAME)

    return 'Succeeded'


# ===============================================================================
def test_authorize_UN_RE_default(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    os.environ['UN_RE_DMV_PSWD'] = 'RE01!?pgpw'

    authorize_UN_RE()

    rows = run_pg_statement("Select 'Hi!';")

    assert rows[0][0] == 'Hi!'

    # If the assertion fails, We will not print the following messages
    print('Sucessfully connected to the PG_DB as expected using {0}.'.format(G.DMV_USERNAME))
    print('        Passed.')


# ===============================================================================
def test_authorize_UN_RE_ro(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    os.environ['UN_RE_DMV_USER'] = 'looker_ro_user'
    os.environ['UN_RE_DMV_PSWD'] = 'AdKz5M3Ly6dQDhrz'

    authorize_UN_RE()

    rows = run_pg_statement("Select 'Hi!';")

    assert rows[0][0] == 'Hi!'

    # If the assertion fails, We will not print the following messages
    print('Sucessfully connected to the PG_DB as expected using {0}.'.format(G.DMV_USERNAME))
    print('        Passed.')
