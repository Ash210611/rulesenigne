import re
import sys

import un_re.global_shared_variables as G
from un_re.print_msg import print_msg


# ======== ========= ========= ========= ========= ========= ========= ==========
def check_for_windows_backslash():
    """
    Make sure the XML file does not use Windows backslash pathnames.

    Will exit the whole procedure if any are found.
    """

    found = False
    with open(G.XML_FILENAME, 'r', encoding='utf-8') as xml_file:
        for line in xml_file.readlines():
            line = line.strip()
            if re.search(r'\\', line, re.IGNORECASE):
                found = True

    if found:
        print_msg('ERROR: The Liquibase XML file is using Windows backslash pathnames.')
        G.LOGGER.error('')
        G.LOGGER.error('Please change the following lines to use forward slashes.')
        with open(G.XML_FILENAME, 'r', encoding='utf-8') as xml_file:
            for line in xml_file.readlines():
                line = line.strip()
                if re.search(r'\\', line, re.IGNORECASE):
                    G.LOGGER.error(line)
        G.LOGGER.error('')
        sys.exit(78)
