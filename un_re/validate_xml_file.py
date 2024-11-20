# pylint: disable=C0209				# Don't require formatted strings

import os
import sys

from lxml import etree

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G

from un_re.check_for_windows_backslash import check_for_windows_backslash
from un_re.indent_info import indent_info
from un_re.print_msg import print_msg


# ======== ========= ========= ========= ========= ========= ========= ==========
def validate_xml_contents(xml_filename):
    '''
    Adapted from this note:
    https://stackoverflow.com/questions/299588/validating-with-an-xml-schema-in-python
    '''

    xsd_filename = G.SCRIPT_DIR + '/un_re/resources/dbchangelog-4.4.xsd'

    try:
        xmlschema_doc = etree.parse(xsd_filename)
        xmlschema = etree.XMLSchema(xmlschema_doc)

        xml_doc = etree.parse(xml_filename)
        result = xmlschema.validate(xml_doc)

    except etree.XMLSyntaxError:
        result = False

    if not result:
        print_msg('Error-xml : The XML file appears invalid')
        sys.exit(E.INVALID_XML_CONTENTS)

    indent_info('Good, the XML file appears valid')


# ======== ========= ========= ========= ========= ========= ========= ==========
def validate_xml_filename(xml_filename):
    """
    Make sure the XML file is found,
    And has no Windows backslash filenames
    And has comments removed if that is the option specified.
    """

    if not os.path.exists(xml_filename):
        G.LOGGER.error('Failed to find the liquibase.xml file.')
        G.LOGGER.error('Tried to find: {0}'.format(xml_filename))
        sys.exit(78)

    check_for_windows_backslash()  # Will exit if any are found


# ===============================================================================
def validate_xml_file(xml_filename):
    validate_xml_filename(xml_filename)
    validate_xml_contents(xml_filename)
