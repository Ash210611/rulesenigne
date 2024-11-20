# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G

from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.check_r241 import find_table_comment
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r243_for_1_table():
    found_an_issue = False
    table_comment = find_table_comment(G.TABLE_STRUCTURE.database_base_upper,
                                       G.TABLE_STRUCTURE.table_name_upper)

    if table_comment is None:
        return found_an_issue
    # If the table comment is completely missing, that
    # is checked by r241

    table_comment = table_comment.strip("'")

    comment_len = len(table_comment)

    if comment_len > 255:

        found_an_issue = True
        report_firm_finding(
            object_type_nm='TABLE COMMENT',
            object_nm=G.TABLE_NAME,
            severity=G.RULES[G.RULE_ID].severity,
            message='{0}.{1} table comment has {2} bytes, which is too long'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                comment_len),
            class_object=G.TABLE_STRUCTURE)

        if comment_len > 62:
            G.LOGGER.info('Table Comment: {0}...'.format(table_comment[:62]))
        else:
            G.LOGGER.info('Table Comment: {0}'.format(table_comment))

    elif G.VERBOSE and len(table_comment.strip()) > 0:
        # Zero-length comments will be reported by R241

        indent_debug('Good         : {0}.{1} table comment is only {2} bytes long.'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper,
            comment_len))

    return found_an_issue


# ===============================================================================
def check_r243():
    """
    The length table comment must be less than 255 characters,
    which is the smallest maximum length allowed length for a DBMS used at
    Cigna.
    """

    G.RULE_ID = 'r243'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_findings = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        if check_r243_for_1_table():
            num_findings += 1

    if num_findings > 1:
        indent_info('Notice       : Found {0} tables with table comments too long.'.format(num_findings))
    elif num_findings == 1:
        indent_info('Notice       : Found {0} table with a table comment too long.'.format(num_findings))
    elif G.VERBOSE:
        indent_debug('Good         : Found no tables with a table comment too long.')
