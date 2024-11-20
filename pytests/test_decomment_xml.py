#
# Run this Unit Test from the parent/project directory using this command:
#       python -B -m pytest pytests/test_decomment_xml.py
#
# ===============================================================================

import inspect
import os
from pathlib import Path

import pytest

import un_re.global_shared_variables as G
from un_re.decomment_xml import decomment_xml
from un_re.fprint import fprint
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
def test_decomment_xml_while_fully_commented(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    with open(G.XML_FILENAME, 'w') as xml_file:
        fprint(xml_file,
               '<!--<databaseChangeLog {0} {1} {2} http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.3.xsd">-->'.format(
                   'xmlns="http://www.liquibase.org/xml/ns/dbchangelog"',
                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
                   'xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog'))

        fprint(xml_file, '<!--<include file="CCW_BASE/Tables/BUS_ENTTY.sql" relativeToChangelogFile="true"/>-->')
        fprint(xml_file, '<!--<changeSet author="Release" id="${project.version}"/>-->')
        fprint(xml_file, '<!--</databaseChangeLog>-->')

    nocom_xml_filename = decomment_xml()

    print('xml_filename = {0}'.format(G.XML_FILENAME))
    print('nocom_xml_filename = {0}'.format(nocom_xml_filename))

    assert nocom_xml_filename != ''

    print('Passed.')  # Can only reach here if the assertion passed


# ===============================================================================
def test_decomment_xml_while_not_commented(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('{0} Running...'.format(this_function_name))

    with open(G.XML_FILENAME, 'w') as xml_file:
        fprint(xml_file,
               '<databaseChangeLog xmlns="http://www.liquibase.org/xml/ns/dbchangelog" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.3.xsd">')
        fprint(xml_file, '<include file="CCW_BASE/Tables/Uncommented.sql" relativeToChangelogFile="true"/>')
        fprint(xml_file, '<changeSet author="Release" id="${project.version}"/>')
        fprint(xml_file, '</databaseChangeLog>')

    nocom_xml_filename = decomment_xml()

    print('xml_filename = {0}'.format(G.XML_FILENAME))
    print('nocom_xml_filename = {0}'.format(nocom_xml_filename))

    assert nocom_xml_filename != ''

    print('Passed.')  # Can only reach here if the assertion passed


# ===============================================================================
def test_decomment_xml_while_partially_commented(setup):
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('{0} Running...'.format(this_function_name))

    with open(G.XML_FILENAME, 'w') as xml_file:
        fprint(xml_file,
               '<databaseChangeLog xmlns="http://www.liquibase.org/xml/ns/dbchangelog" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.3.xsd">')
        fprint(xml_file, '<!--<include file="CCW_BASE/Tables/Commented_1.sql" relativeToChangelogFile="true"/>-->')
        fprint(xml_file, '<include file="CCW_BASE/Tables/Uncommented.sql" relativeToChangelogFile="true"/>')
        fprint(xml_file, '<!--<include file="CCW_BASE/Tables/Commented_2.sql" relativeToChangelogFile="true"/>-->')
        fprint(xml_file, '<changeSet author="Release" id="${project.version}"/>')
        fprint(xml_file, '</databaseChangeLog>')

    nocom_xml_filename = decomment_xml()

    print('xml_filename = {0}'.format(G.XML_FILENAME))
    print('nocom_xml_filename = {0}'.format(nocom_xml_filename))

    assert nocom_xml_filename != ''

    print('Passed.')  # Can only reach here if the assertion passed
