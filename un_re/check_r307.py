# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r307_for_1_table():
    found_an_issue = False

    if G.TABLE_STRUCTURE.command_type != 'CREATE TABLE AS SELECT':
        return found_an_issue

    if len(G.TABLE_STRUCTURE.table_name_tokens) == 0:
        return found_an_issue

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
        return found_an_issue

    if G.TABLE_STRUCTURE.table_name_tokens[0].upper() == 'TEMP':
        if G.VERBOSE:
            indent_info("Good         : The CTAS table name {0} starts with 'TEMP'.".format(
                G.TABLE_STRUCTURE.table_name_upper))
        return found_an_issue

    found_an_issue = True
    report_adjustable_finding(
        object_type_nm='TABLE',
        object_nm=G.TABLE_STRUCTURE.table_name_upper,
        normal_severity=G.RULES[G.RULE_ID].severity,
        normal_message="CTAS table name {0} should start with the 'TEMP' prefix.".format(
            G.TABLE_STRUCTURE.table_name_upper),
        adjusted_message="Accepting CTAS table name {0} not prefixed with 'TEMP' in ruleset {1}".format(
            G.TABLE_STRUCTURE.table_name_upper,
            G.TABLE_STRUCTURE.ruleset),
        class_object=G.TABLE_STRUCTURE)

    return found_an_issue


# ===============================================================================
def check_r307():
    """
    Create Table As Select commands must have a table name that starts
    with TEMP_
    """

    G.RULE_ID = 'r307'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    # Check the rule now that the prerequisites are passed.
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_tables_with_issues = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:
        if check_r307_for_1_table():
            num_tables_with_issues += 1

    if num_tables_with_issues == 1:
        indent_info('Notice-{0}  : {1} CTAS table name does not start with TEMP'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif num_tables_with_issues > 1:
        indent_info('Notice-{0}  : {1} CTAS table names do not start with TEMP.'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif G.VERBOSE:
        indent_debug('Good         : All CTAS table names start with TEMP.')

    return 0
