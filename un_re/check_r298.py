# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r298_for_1_table():
    found_an_issue = False

    if G.TABLE_STRUCTURE.table_name_tokens[0].upper() == 'TMP':
        found_an_issue = True

        report_adjustable_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='{0}.{1} TMP table name should be renamed.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper),
            adjusted_message='Accepting {0}.{1} TMP table name in ruleset {2}'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.TABLE_STRUCTURE.ruleset),
            class_object=G.TABLE_STRUCTURE)

    # else:
    # 	Report a success message if you care about it.

    return found_an_issue


# ===============================================================================
def check_r298():
    """
    Temporary table names should start with TEMP rather than TMP.
    """

    G.RULE_ID = 'r298'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_findings = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            return 0

        if check_r298_for_1_table():
            num_findings += 1

    if num_findings > 1:
        indent_info('Notice       : Found {0} TMP table names that should be renamed.'.format(num_findings))
    elif num_findings == 1:
        indent_info('Notice       : Found {0} TMP table name that should be renamed.'.format(num_findings))
    elif G.VERBOSE:
        indent_debug('Good         : Found no TMP table names.')

    return 0
