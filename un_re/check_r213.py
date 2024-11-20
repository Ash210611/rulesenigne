# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_old_business_terms import check_for_old_business_terms
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info


# ===============================================================================
def check_r213_for_1_table():
    # Iterate on table columns

    num_columns_with_issues = 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
        return num_columns_with_issues

    if G.TABLE_STRUCTURE.table_name_tokens[0].upper() in ('W', 'TEMP', 'TMP'):
        # Skip this rule for work tables.
        indent_debug('Notice-{0}  : Skipping {0} for a Work table: {1}'.format(
            G.RULE_ID,
            G.TABLE_STRUCTURE.table_name_upper))
        return num_columns_with_issues

    G.COLUMN_ELEMENTS = G.TABLE_STRUCTURE.column_elements

    for G.COLUMN_ELEMENT in G.COLUMN_ELEMENTS:
        if check_for_rule_exception(G.RULE_ID,
                                    G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper,
                                    G.COLUMN_ELEMENT.name_upper):
            if G.VERBOSE:
                indent_debug('Notice-{0}  : Skipping column {1}.{2}'.format(
                    G.RULE_ID,
                    G.TABLE_STRUCTURE.table_name_upper,
                    G.COLUMN_ELEMENT.name_upper))
            continue

        this_object_name = f'{G.TABLE_STRUCTURE.database_base_upper}' + \
                           f'.{G.TABLE_STRUCTURE.table_name_upper}' + \
                           f'.{G.COLUMN_ELEMENT.name_upper}'

        if check_for_old_business_terms('Column name',
                                        G.COLUMN_ELEMENT.name_upper,
                                        G.COLUMN_ELEMENT.column_name_tokens,
                                        this_object_name):
            num_columns_with_issues += 1

    if G.VERBOSE:
        if not G.COLUMN_ELEMENTS:
            indent_debug('Good         : Table {0} has 0 columns with an obsolete business term.'.format(
                G.TABLE_STRUCTURE.table_name_upper))
        elif num_columns_with_issues == 0:
            indent_debug('Good         : Table {0} has {1} columns without an obsolete business term.'.format(
                G.TABLE_STRUCTURE.table_name_upper,
                len(G.COLUMN_ELEMENTS)))

    return num_columns_with_issues


# ===============================================================================
def check_r213():
    """
    This function checks that column names do not contain obsolete business
    terms.
    """

    G.RULE_ID = 'r213'

    # -----------------------------------------------------------------------

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    # Iterate through tables
    # -----------------------------------------------------------------------

    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_tables_with_issues = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_r213_for_1_table() > 0:
            num_tables_with_issues += 1

    if num_tables_with_issues == 1:
        indent_info('Notice-{0}  : {1} table has one or more column names with an obsolete business term'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif num_tables_with_issues > 1:
        indent_info('Notice-{0}  : {1} tables have one or more column names with an obsolete business term.'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif G.VERBOSE:
        indent_debug('Good         : No tables have any columns with obsolete business terms.')

    return 0
