# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r457_for_1_table():
    found_an_issue = False

    pattern = re.compile('FALLBACK', re.IGNORECASE)
    if pattern.search(G.TABLE_STRUCTURE.sql_stmt_txt):
        found_an_issue = True

        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='Table {0}.{1} should not be FALLBACK.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper),
            class_object=G.TABLE_STRUCTURE)

        # Print that line for context
        for line in G.TABLE_STRUCTURE.sql_stmt_txt.split('\n'):
            if pattern.search(line):
                indent_info(line)

    return found_an_issue


# ===============================================================================
def check_r457():
    G.RULE_ID = 'r457'

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_findings = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        if check_r457_for_1_table():
            num_findings += 1

    if num_findings > 1:
        indent_info('Notice       : Found {0} tables that should not be Fallback.'.format(num_findings))
    elif num_findings == 1:
        indent_info('Notice       : Found 1 table that should not be Fallback.')
    elif G.VERBOSE:
        indent_debug('Good         : Found no tables that are Fallback.')
