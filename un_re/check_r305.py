import un_re.global_shared_variables as G
from un_re.binary_search import binary_search
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.print_msg import print_msg


# ===============================================================================
def check_r305(column_name):
    """
    This function will check that the table name is found in the list
    of CCW_BASE column names.
    """

    G.RULE_ID = 'r305'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if G.COMMAND_TYPE != 'CREATE TABLE':
        return 0

    if check_for_rule_exception(G.RULE_ID):
        return 0

    # -----------------------------------------------------------------------
    found = binary_search(G.CCW_BASE_COLUMNNAME_LIST, column_name.upper())

    if not found:
        print_msg('WARNING-r305 : Column name {column_name} is not found in the list of CCW_BASE column names')

    elif G.VERBOSE:
        indent_debug(f'Good         : Column name {column_name} is found in the list of CCW_BASE column names')

    return 0
