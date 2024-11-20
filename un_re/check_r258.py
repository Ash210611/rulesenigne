# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G

from un_re.check_articles import check_articles
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info


# ===============================================================================
def check_r258_for_1_table():
    found_an_issue = False

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
        return found_an_issue

    if G.TABLE_STRUCTURE.table_name_tokens[0].upper() in ('W', 'TEMP', 'TMP'):
        # Skip this rule for work tables.
        indent_debug(f'Notice-{G.RULE_ID}  : Skipping {G.RULE_ID} for a Work table.')
        return found_an_issue

    # -----------------------------------------------------------------------
    found_an_issue = check_articles(
        'Table name',
        G.TABLE_STRUCTURE.table_name_upper,
        G.TABLE_STRUCTURE.table_name_tokens,
        G.RULE_ID,
        G.TABLE_STRUCTURE.ruleset)

    if not found_an_issue and G.VERBOSE:
        indent_debug('Good         : Table name {0} does not contain an article.'.format(
            G.TABLE_STRUCTURE.table_name_upper))

    return found_an_issue


# ===============================================================================
def check_r258():
    """
    This function checks that table names do not contain articles.
    """

    G.RULE_ID = 'r258'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_tables_with_issues = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_r258_for_1_table():
            num_tables_with_issues += 1

    if num_tables_with_issues == 1:
        indent_info('Notice-{0}  : {1} table name has an article.'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif num_tables_with_issues > 1:
        indent_info('Notice-{0}  : {1} table names have an article.'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif G.VERBOSE:
        indent_debug('Good         : No table names have an article.')

    return 0
