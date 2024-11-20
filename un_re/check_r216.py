# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G

from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.check_r217 import check_r217_for_1_column
from un_re.find_classword import find_classword
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r216_for_one_column():
    G.COLUMN_NAME = G.COLUMN_ELEMENT.name_upper
    # G.DATATYPE             = G.COLUMN_ELEMENT.datatype

    if G.COLUMN_ELEMENT.column_name_tokens[0].upper() == 'SRC':
        G.COLUMN_ELEMENT.classword = ''
        if G.VERBOSE:
            indent_debug('Notice       : {0}.{1}.{2} skipping {3} for a SRC column'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_NAME,
                G.RULE_ID))
        return True  # Don't check classwords and datatypes for SRC columns

    if check_r217_for_1_column(G.COLUMN_NAME):
        G.COLUMN_ELEMENT.classword = ''
        return True  # This column has a classword exception

    classword = find_classword(G.COLUMN_ELEMENT.naming_method, G.COLUMN_ELEMENT.column_name_tokens)

    if classword is None:
        report_adjustable_finding(
            object_type_nm='COLUMN',
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
        G.COLUMN_ELEMENT.classword = classword

        if G.VERBOSE:
            indent_debug('Good         : {0}.{1}.{2} uses classword {3}'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_NAME,
                classword))

    return classword is not None


# will return false if no valid classword is found and no exception is found
# will return true if it found a valid classword or an exception

# ===============================================================================
def check_r216_for_1_table():
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

        if not check_r216_for_one_column():
            num_columns_with_issues += 1

    if num_columns_with_issues == 0:
        if G.VERBOSE:
            indent_debug('Good         : All {0} column names in {1} are using a valid classword.'.format(
                len(G.COLUMN_ELEMENTS),
                G.TABLE_STRUCTURE.table_name_upper))

    return num_columns_with_issues


# ===============================================================================
def check_r216():
    """
    Columns names must include a valid classword.
    """

    G.RULE_ID = 'r216'

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
                indent_debug('Notice-{0}  : Skipping {0} for {1} as a Work table.'.format(
                    G.RULE_ID,
                    G.TABLE_STRUCTURE.table_name_upper))
            continue

        if check_r216_for_1_table() > 0:
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
