# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G

from un_re.binary_search import binary_search
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r003_for_one_column():
    G.COLUMN_NAME = G.COLUMN_ELEMENT.name_upper

    if G.COLUMN_ELEMENT.column_name_tokens[0].upper() == 'SRC':
        G.COLUMN_ELEMENT.classword = ''
        if G.VERBOSE:
            indent_debug('Notice       : {0}.{1}.{2} skipping {3} for a SRC column'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_NAME,
                G.RULE_ID))
        return True  # Don't check classwords and datatypes for SRC columns

    found_a_classword = False
    column_part = ''  # Initialize for pylint
    for column_part in reversed(G.COLUMN_ELEMENT.column_name_tokens):
        # Take the classword most towards the end of the column name

        column_part = column_part.upper()
        if G.COLUMN_ELEMENT.naming_method == 'SNAKE_CASE':
            found_a_classword = binary_search(G.PHYSICAL_CLASSWORD_LIST, column_part)
        elif G.COLUMN_ELEMENT.naming_method == 'MixedCase':
            found_a_classword = binary_search(G.LOGICAL_CLASSWORD_LIST, column_part)

        if found_a_classword:
            break

    if not found_a_classword:
        if G.COLUMN_ELEMENT.name_upper in G.PHYSICAL_CLASSWORD_EXCEPTION_LIST:
            indent_info('Notice       : Column name {0}.{1}.{2} is approved to not need a valid classword.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_ELEMENT.name_upper))
            return True

    if not found_a_classword:
        report_adjustable_finding(
            object_type_nm='TABLE',
            object_nm='{0}.{1}.{2}'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_NAME.strip('"')),
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='No valid classword found in column name {0}.{1}.{2}'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_ELEMENT.name_upper),
            adjusted_message=
            'Column name {0}.{1}.{2} accepted without a valid classword in ruleset {3}.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_ELEMENT.name_upper,
                G.TABLE_STRUCTURE.ruleset),
            class_object=G.TABLE_STRUCTURE)

    else:  # Save the classword for future reference
        G.COLUMN_ELEMENT.classword = column_part

        if G.VERBOSE:
            indent_debug('Good         : {0}.{1}.{2} uses classword {3}'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_NAME,
                column_part))

    return found_a_classword


# will return false if no valid classword is found and no exception is found
# will return true if it found a valid classword or an exception

# ===============================================================================
def check_r003_for_1_table():
    num_columns_with_issues = 0
    if len(G.TABLE_STRUCTURE.column_elements) == 0:
        indent_debug('Good         : {0} has no columns to check for a valid classword.'.format(
            G.TABLE_STRUCTURE.table_name_upper))
        return num_columns_with_issues

    G.COLUMN_ELEMENTS = G.TABLE_STRUCTURE.column_elements

    for G.COLUMN_ELEMENT in G.COLUMN_ELEMENTS:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper, G.COLUMN_ELEMENT.name_upper):
            continue

        if not check_r003_for_one_column():
            num_columns_with_issues += 1

    if num_columns_with_issues == 0:
        if G.VERBOSE:
            num_cols = len(G.COLUMN_ELEMENTS)
            if num_cols > 1:
                indent_debug('Good         : All {0} column names in {1} are using a valid classword.'.format(
                    len(G.COLUMN_ELEMENTS),
                    G.TABLE_STRUCTURE.table_name_upper))
            elif num_cols == 1:
                indent_debug('Good         : The column in {0} is using a valid classword.'.format(
                    G.TABLE_STRUCTURE.table_name_upper))

    return num_columns_with_issues


# ===============================================================================
def check_r003():
    """
    Columns names must include a valid classword.
    """

    G.RULE_ID = 'r003'

    # -----------------------------------------------------------------------
    # Check prerequisites

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

        if G.TABLE_STRUCTURE.table_name_tokens[0].upper() in ('W', 'TEMP', 'TMP'):

            # Skip this rule for work tables.
            if G.VERBOSE:
                indent_debug('Notice-{0}  : Skipping {0} for a Work table.'.format(
                    G.RULE_ID))
            continue

        if check_r003_for_1_table() > 0:
            num_tables_with_issues += 1

    if num_tables_with_issues == 1:
        indent_info('Notice-{0}  : {1} table has one or more column names without a valid classword.'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif num_tables_with_issues > 1:
        indent_info('Notice-{0}  : {1} tables have one or more column names without a valid classword.'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif G.VERBOSE:
        indent_debug('Good         : All column names in all tables have valid classwords.')

    return 0
