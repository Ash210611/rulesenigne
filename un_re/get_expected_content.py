# pylint: disable=C0209			# Don't require formatted strings.

import os
import sys
from collections import OrderedDict

import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.print_msg import print_msg


# ===============================================================================
def get_expected_content():
    """
    For now this is reading from a static table.

    """
    G.RULE_ID = 'r401'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if not os.path.exists(G.Z_FILE):
        print_msg('Error: Unable to find the z file.')
        G.LOGGER.error('               Tried to find {0}'.format(G.Z_FILE))
        sys.exit(12)

    od = OrderedDict()

    with open(G.Z_FILE, 'r', encoding='utf-8') as word_file:
        for line in word_file.readlines():
            line = line.strip()
            od[line] = True

    G.EXPECTED_CONTENT = list(sorted(od.keys()))

    if G.VERBOSE:
        indent('Read {0:5,d} expected items.'.format(
            len(G.EXPECTED_CONTENT)))
