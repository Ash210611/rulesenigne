#
# Run this Unit Test from the parent/project directory using this command:
#       python -B -m pytest pytests/test_dreml_get_list_of_dml_files.py
#
# ===============================================================================

import inspect
import os
from pathlib import Path

import pytest

import un_re.global_shared_variables as G
from un_re.dreml_get_list_of_dml_files import read_versions_file
from un_re.fprint import fprint
from un_re.setup_logging import setup_logging


# ===============================================================================
@pytest.fixture
def setup(tmpdir_factory):
    G.SHA_LIST = []
    G.RULES_ENGINE_TYPE = 'TERADATA_DML'

    G.SCRIPT_DIR = str(Path(os.path.dirname(__file__)).parent)

    G.TEMP_DIR = tmpdir_factory.mktemp("logs")
    G.VERSIONS_FILENAME = os.path.join(G.TEMP_DIR, "feature.versions")

    G.LOG_FILENAME = os.path.join(G.TEMP_DIR, "junk.log")
    setup_logging(G.LOG_FILENAME)

    G.POSTGRES_JSON_FILENAME = os.path.join(G.TEMP_DIR, "postgres.json")
    G.ERROR_FILENAME = os.path.join(G.TEMP_DIR, 'Rules_Engine.errors')


# ===============================================================================
def test_read_versions_file_w_merge_conflict(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    with open(G.VERSIONS_FILENAME, 'w') as ver_file:
        fprint(ver_file, '')
        fprint(ver_file, 'path1_WI00613_mavenized=path1_WI00613_mavenized.45.48043751')
        fprint(ver_file, 'path1_WI00120319_REF_BED_DAYS_0621=path1_WI00120319_REF_BED_DAYS_0621.137.259fa45a')
        fprint(ver_file, '<<<<<<< HEAD')
        fprint(ver_file, 'path1_WI00202666_RXI_ESI2_REF_1030=path1_WI00202666_RXI_ESI2_REF_1030.3415.d8b9aaab')
        fprint(ver_file, '=======')
        fprint(ver_file, 'path1_WI00203010_CCW_ESI2_REF_1022=path1_WI00203010_CCW_ESI2_REF_1022.3592.e5efa138')
        fprint(ver_file, 'path1_WI00203010_CCW_ESI2_REF_1022_previous=path1_WI00203010_CCW_ESI2_REF_1022.3563.21eb05bc')
        fprint(ver_file, '>>>>>>> path1_WI00203010_CCW_ESI2_REF_1022')

    read_versions_file(G.VERSIONS_FILENAME)

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

    print('        Passed.')  # Can only reach here if the assertion passed


# ===============================================================================
def test_read_versions_file_w_dots(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    with open(G.VERSIONS_FILENAME, 'w') as ver_file:
        fprint(ver_file, '')
        fprint(ver_file, 'path1_WI00613_mavenized=path1_WI00613_mavenized.45.48043751')
        fprint(ver_file, 'path1_WI00213279_GHTR_PHRM=path1_WI00213279_GHTR_PHRM.5016.481aea66')
        fprint(ver_file, 'path1_WI00213279_GHTR_PHRM_previous=path1_WI00213279_GHTR_PHRM.5014.26f8aa01')
        fprint(ver_file, 'path1_WI00218099_CVD_EXT_PI21.3.1=path1_WI00218099_CVD_EXT_PI21.3.1.5047.a0781444')

    read_versions_file(G.VERSIONS_FILENAME)  # populates G.SHA_LIST

    # Check for expected output
    found_no_error_as_expected = True
    if os.path.exists(G.ERROR_FILENAME):
        found_no_error_as_expected = False
        with open(G.ERROR_FILENAME, 'r') as f:
            print('=' * 80)
            print('Error file found unexpectedly:')
            print('')
            for line in f.readlines():
                line = line.strip()
                print(line)
            print('=' * 80)

    assert found_no_error_as_expected

    print('        Passed.')  # Can only reach here if the assertion passed
    print('SHA_LIST = {0}'.format(G.SHA_LIST))
