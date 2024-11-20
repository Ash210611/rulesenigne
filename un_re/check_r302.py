# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.binary_search import binary_search
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.print_msg import print_msg


# ===============================================================================
def check_r302():
    """
    This function will check that each part of a table name is found
    in the list of Enterprise Naming Standards
    """

    G.RULE_ID = 'r302'

    # -----------------------------------------------------------------------

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if G.COMMAND_TYPE not in ('CREATE TABLE', 'CREATE TABLE AS SELECT'):
        return 0

    if check_for_rule_exception(G.RULE_ID):
        return 0

    # -----------------------------------------------------------------------
    all_found = True
    for fragment in G.TABLE_NAME_PART_LIST:

        if fragment == '':
            # It came from 2 consecutive underscores.
            continue

        fragment = fragment.upper()
        found = binary_search(G.ENTERPRISE_NAMING_STANDARD, fragment)

        if not found:
            if str.isdigit(fragment):
                if G.VERBOSE:
                    indent_debug('Notice       : The table name fragment {0} is an integer'.format(
                        fragment))

            else:
                print_msg('WARNING-r302 : Table name {0} fragment {1} not found in Enterprise Naming Standard'.format(
                    G.TABLE_NAME,
                    fragment))
                all_found = False

        elif G.VERBOSE:
            G.LOGGER.debug((' ' * 15) + \
                           'Good         : The table name fragment {0} is found in the Enterprise Naming Standard'.format(
                               fragment))

    if all_found and G.VERBOSE:
        G.LOGGER.debug(
            (' ' * 15) + 'Good         : All table name fragments are found in the Enterprise Naming Standard.')

    return 0
