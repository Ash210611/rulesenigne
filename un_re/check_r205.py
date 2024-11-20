# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_bad_characters import check_for_bad_characters
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r205_for_1_table():
    num_found_for_this_table = 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
        print(f'Skipping table {G.TABLE_STRUCTURE.table_name_upper}')
        return 0

    # Skip this rule for work tables.
    if G.TABLE_STRUCTURE.table_name_tokens:
        if G.TABLE_STRUCTURE.table_name_tokens[0].upper() in ('W', 'TEMP', 'TMP'):

            if G.VERBOSE:
                indent_debug('Notice-{0}  : Skipping Work table: {1}'.format(
                    G.RULE_ID,
                    G.TABLE_STRUCTURE.table_name_upper))
                return 0
    else:
        if G.VERBOSE:
            indent_debug('Notice-{0}  : Skipping {0} with no tokens for table {1}.'.format(
                G.RULE_ID,
                G.TABLE_STRUCTURE.table_name_upper))
        return 0

    G.COLUMN_ELEMENTS = G.TABLE_STRUCTURE.column_elements

    for G.COLUMN_ELEMENT in G.COLUMN_ELEMENTS:
        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper,
                                    G.COLUMN_ELEMENT.name_upper):
            continue

        msg = check_for_bad_characters(G.COLUMN_ELEMENT.name_upper)
        if msg != '':
            num_found_for_this_table += 1

            report_adjustable_finding(object_type_nm='column name',
                                      object_nm=G.COLUMN_ELEMENT.name_upper,
                                      normal_severity=G.RULES[G.RULE_ID].severity,
                                      normal_message="The column name for {0}.{1} should not contain {2}.".format(
                                          G.TABLE_STRUCTURE.table_name_upper,
                                          G.COLUMN_ELEMENT.name_upper,
                                          msg),
                                      adjusted_message='Accepting {0} in column_name{1}.{2} for ruleset {3}.'.format(
                                          msg,
                                          G.TABLE_STRUCTURE.table_name_upper,
                                          G.COLUMN_ELEMENT.name_upper,
                                          G.TABLE_STRUCTURE.ruleset),
                                      class_object=G.TABLE_STRUCTURE)

    if num_found_for_this_table == 0 and G.VERBOSE:
        indent_debug('Good         : {0}.{1} has no column names with bad characters.'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper))

    return num_found_for_this_table


# ===============================================================================
def check_r205():
    """
    Column names should not have bad characters
    """
    G.RULE_ID = 'r205'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0
    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_tables_with_issues = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_r205_for_1_table() > 0:
            num_tables_with_issues += 1

    if num_tables_with_issues == 1:
        indent_info('Notice-{0}  : {1} table has one or more column names with bad characters.'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif num_tables_with_issues > 1:
        indent_info(
            f'Notice-{G.RULE_ID}  : ' +
            f'{num_tables_with_issues} tables have one or more column names with bad characters.')

    elif G.VERBOSE:
        indent_debug('Good         : No tables have any column names with bad characters.')

    return 0
