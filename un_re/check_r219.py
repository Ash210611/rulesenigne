# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G

from un_re.check_articles import check_articles
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info


# ===============================================================================
def check_r219_for_1_column():
    found_an_issue = False

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME,
                                G.TABLE_STRUCTURE.table_name_upper, G.COLUMN_ELEMENT.name_upper):
        return found_an_issue

    # -----------------------------------------------------------------------
    # Check the rule

    found_an_issue = check_articles('Column name',
                                    G.TABLE_STRUCTURE.table_name_upper + '.' + G.COLUMN_ELEMENT.name_upper,
                                    G.COLUMN_ELEMENT.column_name_tokens,
                                    G.RULE_ID,
                                    G.TABLE_STRUCTURE.ruleset)

    return found_an_issue


# ===============================================================================
def check_r219_for_1_table():
    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
        return 0

    if G.TABLE_STRUCTURE.table_name_tokens[0].upper() in ('W', 'TEMP', 'TMP'):
        # Skip this rule for work tables.
        G.LOGGER.debug((' ' * 15) + 'Notice-{0}  : Skipping {0} for a Work table.'.format(G.RULE_ID))
        return 0

    G.COLUMN_ELEMENTS = G.TABLE_STRUCTURE.column_elements

    num_columns_with_an_issue = 0
    for G.COLUMN_ELEMENT in G.COLUMN_ELEMENTS:

        if check_r219_for_1_column():
            num_columns_with_an_issue += 1

    return num_columns_with_an_issue


# ===============================================================================
def check_r219():
    """
    This function checks that column names do not contain articles.
    """
    ret = ''

    G.RULE_ID = 'r219'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_tables_with_issues = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_r219_for_1_table() > 0:
            num_tables_with_issues += 1

    if num_tables_with_issues == 1:
        indent_info('Notice-{0}  : {1} table has one or more columns names with an article.'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif num_tables_with_issues > 1:
        indent_info('Notice-{0}  : {1} tables have one or more column names with an article.'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif G.VERBOSE:
        indent_debug('Good         : No tables have any column names with an article.')

    return ret
