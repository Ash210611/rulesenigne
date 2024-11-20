#
# Run this Unit Test from the parent/project directory using this command:
#       python -B -m pytest pytests/test_read_the_list_of_input_SQL_files_from_xml_file.py
#
# ===============================================================================

import inspect
import os
from pathlib import Path

import pytest

import un_re.global_shared_variables as G
from un_re.fprint import fprint
from un_re.read_the_list_of_input_files import read_the_input_filenames_from_xml_file
from un_re.setup_logging import setup_logging


# ===============================================================================
@pytest.fixture
def setup(tmpdir_factory):
    G.RULES_ENGINE_TYPE = 'TERADATA_DDL'

    G.SCRIPT_DIR = str(Path(os.path.dirname(__file__)).parent)

    G.TEMP_DIR = tmpdir_factory.mktemp("logs")
    G.XML_FILENAME = os.path.join(G.TEMP_DIR, "junk.xml")

    G.LOG_FILENAME = os.path.join(G.TEMP_DIR, "junk.log")
    setup_logging(G.LOG_FILENAME)

    G.POSTGRES_JSON_FILENAME = os.path.join(G.TEMP_DIR, "postgres.json")
    G.ERROR_FILENAME = os.path.join(G.TEMP_DIR, 'Rules_Engine.errors')


# ===============================================================================
def test_xml_1(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    with open(G.XML_FILENAME, 'w') as xml_file:
        fprint(xml_file,
               '<!--<databaseChangeLog {0} {1} {2} http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.3.xsd">-->'.format(
                   'xmlns="http://www.liquibase.org/xml/ns/dbchangelog"',
                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
                   'xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog'))

        fprint(xml_file,
               '<!--<include file="CCW_LZ/Tables/PHRMRDS_PHRM_CLM_PROG_IDNTY_MV.sql" relativeToChangelogFile="true"/>-->')
        fprint(xml_file, '<include file="CCW_STG/Tables/TEMP_PHRMRDS_PHRM_CLM_1.sql" relativeToChangelogFile="true"/>')
        fprint(xml_file,
               '<!--<include file="CCW_STG/Tables/W_PHRMRDS_CLM_PHRM.sql" relativeToChangelogFile="true"/>-->')

        fprint(xml_file, '<!--<changeSet author="Release" id="${project.version}"/>-->')
        fprint(xml_file, '<!--</databaseChangeLog>-->')

    input_filenames = read_the_input_filenames_from_xml_file(
        G.XML_FILENAME,
        check_existence=False)  # for testing purposes, usually True

    num_input_filenames = len(input_filenames)
    print(f'    Num input_filenames: {num_input_filenames}')
    for i, input_filename in enumerate(input_filenames):
        print(f'        Filename {i + 1}: {input_filename}')

    assert num_input_filenames == 1

    print('        Passed.')  # Can only reach here if the assertion passed


# ===============================================================================
def test_xml_2(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    with open(G.XML_FILENAME, 'w') as xml_file:
        fprint(xml_file,
               '<!--<databaseChangeLog {0} {1} {2} http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.3.xsd">-->'.format(
                   'xmlns="http://www.liquibase.org/xml/ns/dbchangelog"',
                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
                   'xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog'))

        fprint(xml_file,
               '<!--<include file="CCW_LZ/Tables/PHRMRDS_PHRM_CLM_COPAY_ASTNC_MV.sql" relativeToChangelogFile="true"/>-->')
        fprint(xml_file,
               '<!-- <include file="CCW_LZ/Tables/PHRMRDS_PHRM_CLM_COPAY_ASTNC_MV_BAK.sql" relativeToChangelogFile="true"/> -->')
        fprint(xml_file,
               '<!--<include file="CCW_STG/Tables/TEMP_CLPA_NRT_INCR_KEYS.sql" relativeToChangelogFile="true"/>-->')

        fprint(xml_file, '<!--<changeSet author="Release" id="${project.version}"/>-->')
        fprint(xml_file, '<!--</databaseChangeLog>-->')

    input_filenames = read_the_input_filenames_from_xml_file(
        G.XML_FILENAME,
        check_existence=False)  # for testing purposes, usually True

    num_input_filenames = len(input_filenames)
    print(f'    Num input_filenames: {num_input_filenames}')
    for i, input_filename in enumerate(input_filenames):
        print(f'        Filename {i + 1}: {input_filename}')

    assert num_input_filenames == 0

    print('        Passed.')  # Can only reach here if the assertion passed
