# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r406_for_1_view():
    pattern = re.compile(r'(lock|locking) row.*( for| in)? access', re.IGNORECASE)

    found_issue = False
    if not pattern.search(G.VIEW_STRUCTURE.sql_stmt_txt):

        report_firm_finding(
            object_type_nm='VIEW',
            object_nm=G.VIEW_STRUCTURE.view_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='{0}.{1} does not specify "Locking row for access"'.format(
                G.VIEW_STRUCTURE.database_base_upper,
                G.VIEW_STRUCTURE.view_name_upper),
            class_object=G.VIEW_STRUCTURE)

        found_issue = True
    # G.LOGGER.info ('Here are the the first 10 lines of the file contents being checked.')
    # for line in G.SQL_STATEMENT.split ('\n'):
    # 	G.LOGGER.info (line.strip ())

    elif G.VERBOSE:

        indent_debug('Good         : View {0}.{1} specifies locking row for access.'.format(
            G.VIEW_STRUCTURE.database_base_upper,
            G.VIEW_STRUCTURE.view_name_upper))

    return found_issue


# ===============================================================================
def check_r406():
    """
    This function will check views to make sure they say
        "locking row for access"
    """

    G.RULE_ID = 'r406'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    total_num_issues = 0
    for G.VIEW_STRUCTURE in G.VIEW_STRUCTURES:
        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.VIEW_STRUCTURE.view_name_upper):
            return 0

        if check_r406_for_1_view():
            total_num_issues += 1

    if total_num_issues > 1:

        indent_info('Notice       : Found {0} views with locking issues'.format(total_num_issues))

    elif total_num_issues == 1:

        indent_info('Notice       : Found {0} view with locking issues'.format(total_num_issues))

    elif G.VERBOSE:

        indent_info('Good         : Found {0} views with locking issues'.format(total_num_issues))

    return 0
