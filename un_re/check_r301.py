# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G

from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r301_for_1_column(table_name, column_name):
    found_an_issue = False

    column_name_len = len(column_name)
    if column_name_len > G.NAME_LENGTH_LIMIT:
        found_an_issue = True
        report_firm_finding(
            object_type_nm='COLUMN',
            object_nm=column_name,
            severity=G.RULES[G.RULE_ID].severity,
            message='The column name length is {0} (>{3}) for {1}.{2}'.format(
                column_name_len,
                table_name,
                column_name,
                G.NAME_LENGTH_LIMIT),
            class_object=G.TABLE_STRUCTURE)

    # This does not need to be reported verbosely

    return found_an_issue


# ===============================================================================
def check_r301_for_1_table():
    G.COLUMN_ELEMENTS = G.TABLE_STRUCTURE.column_elements

    num_columns_with_issues = 0

    for G.COLUMN_ELEMENT in G.COLUMN_ELEMENTS:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper,
                                    G.COLUMN_ELEMENT.name_upper):
            continue

        if check_r301_for_1_column(
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_ELEMENT.name_upper):
            num_columns_with_issues += 1

    return num_columns_with_issues


# ===============================================================================
def check_r301():
    """
    Column names should be N characters or less.

    The number limit is set by the G.NAME_LENGTH_LIMIT variable
    """

    G.RULE_ID = 'r301'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_tables_with_issues = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:
        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        if check_r301_for_1_table() > 0:
            num_tables_with_issues += 1

    if num_tables_with_issues == 1:
        indent_info('Notice-{0}  : {1} table has one or more column names that are too long'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif num_tables_with_issues > 1:
        indent_info('Notice-{0}  : {1} tables have one or more column names that are too long.'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif G.VERBOSE:
        indent_debug('Good         : No tables have any columns that are too long.')

    return 0
