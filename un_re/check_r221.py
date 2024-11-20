# pylint: disable=C0209           # Don't require formtted strings

import un_re.class_definitions as C
import un_re.global_shared_variables as G

from un_re.binary_search import binary_search
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r221_digit_part_num():
    '''
    Check if there is an array digit anywhere in the column name

    Take the digit most towards the end of the column name

    return -1 if no digit is found
    '''

    num_column_tokens = len(G.COLUMN_NAME_PART_LIST)
    digit_part_num = num_column_tokens - 1

    while digit_part_num >= 0:
        column_part = G.COLUMN_NAME_PART_LIST[digit_part_num]

        if column_part.isdigit():
            return digit_part_num

        digit_part_num -= 1

    # If here, there is no digit in that string.
    return digit_part_num


# ===============================================================================
def check_r221_classword_part_num():
    '''
    Take the classword most towards the end of the column name

    Choose the last one found
    '''

    num_column_name_parts = len(G.COLUMN_NAME_PART_LIST)
    classword_part_num = num_column_name_parts - 1

    while classword_part_num >= 0:

        column_part = G.COLUMN_NAME_PART_LIST[classword_part_num].upper()

        if G.TABLE_STRUCTURE.naming_method == 'SNAKE_CASE':
            found_classword = binary_search(G.PHYSICAL_CLASSWORD_LIST, column_part)
        elif G.TABLE_STRUCTURE.naming_method == 'MixedCase':
            found_classword = binary_search(G.LOGICAL_CLASSWORD_LIST, column_part)
        else:
            found_classword = False

        if found_classword:
            return classword_part_num

        classword_part_num -= 1

    return classword_part_num


# ===============================================================================
def check_r221_for_1_column():
    G.COLUMN_NAME_PART_LIST = G.COLUMN_ELEMENT.column_name_tokens

    digit_part_num = check_r221_digit_part_num()

    if digit_part_num < 0:
        # This will be the case almost all the time.
        return False  # Did not find an issue

    # -----------------------------------------------------------------------
    # Since a digit exists, find the last classword

    found_an_issue = False

    classword_part_num = check_r221_classword_part_num()
    if classword_part_num < 0:
        return found_an_issue  # Return False
    # -----------------------------------------------------------------------

    if digit_part_num > classword_part_num:
        if G.VERBOSE:
            indent_debug('Good         : {0} The array digit follows the classword, {1}.'.format(
                G.COLUMN_ELEMENT.name_upper,
                G.COLUMN_NAME_PART_LIST[classword_part_num]))

    elif digit_part_num < classword_part_num - 1:

        if G.VERBOSE:
            indent_debug('Good         : {0} The array index comes far enough before the classword, {1}.'.format(
                G.COLUMN_ELEMENT.name_upper,
                G.COLUMN_NAME_PART_LIST[classword_part_num].upper()))

    elif G.COLUMN_ELEMENT.classword in ('LMT', 'PCTL'):

        if G.VERBOSE:
            indent_debug('Notice       : Accepting {0} numeric interpretation for {1}.'.format(
                G.COLUMN_ELEMENT.classword,
                G.COLUMN_ELEMENT.name_upper))

    else:
        comparison_obj = C.ArrayException(G.COLUMN_ELEMENT.name_upper, None, None)

        found_exception = binary_search(G.ARRAY_EXCEPTION_LIST, comparison_obj)

        if found_exception:
            if G.VERBOSE:
                indent_debug('Notice       : {0} is an exception to the array number rule.'.format(
                    G.COLUMN_ELEMENT.name_upper))

        else:
            found_an_issue = True

            report_adjustable_finding(
                object_type_nm='COLUMN',
                object_nm=G.COLUMN_ELEMENT.name_upper,
                normal_severity=G.RULES[G.RULE_ID].severity,
                normal_message='{0}.{1}.{2} should have the array number follow the classword, {3}.'.format(
                    G.TABLE_STRUCTURE.database_base_upper,
                    G.TABLE_STRUCTURE.table_name_upper,
                    G.COLUMN_ELEMENT.name_upper,
                    G.COLUMN_ELEMENT.classword),
                adjusted_message='Accepting array exception for {0}.{1}.{2} in ruleset {3}.'.format(
                    G.TABLE_STRUCTURE.database_base_upper,
                    G.TABLE_STRUCTURE.table_name_upper,
                    G.COLUMN_ELEMENT.name_upper,
                    G.TABLE_STRUCTURE.ruleset),
                class_object=G.TABLE_STRUCTURE)

    return found_an_issue


# ===============================================================================
def check_r221_for_1_table():
    G.COLUMN_ELEMENTS = G.TABLE_STRUCTURE.column_elements

    num_columns_with_issues = 0

    if G.VERBOSE:
        indent_debug((' ' * 15) + 'Checking array column indexes for {0}.{1}...'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper))

    for G.COLUMN_ELEMENT in G.COLUMN_ELEMENTS:

        if check_r221_for_1_column():
            num_columns_with_issues += 1

    return num_columns_with_issues > 0


# ===============================================================================
def check_r221():
    """
    Array columns names must have the digit follow the classword.

    Classwords are checked in a separate function, so that each rule
    can be turned on and off separately.

    If a column name has a digit in the name somewhere, the position must
    come after the position of the keyword, or it must come earlier in the
    column name, not right before the column name..
    """

    G.RULE_ID = 'r221'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_tables_with_issues = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        if G.TABLE_STRUCTURE.table_name_tokens[0].upper() in ('W', 'TEMP', 'TMP'):
            # Skip this rule for work tables.
            indent_info('Notice-{0}  : Skipping {0} for a Work table.'.format(
                G.RULE_ID))
            continue

        if check_r221_for_1_table():
            num_tables_with_issues += 1

    if num_tables_with_issues > 1:
        indent_info('Notice       : Found {0} tables have misnumbered array columns.'.format(num_tables_with_issues))
    elif num_tables_with_issues == 1:
        indent_info('Notice       : Found {0} table has a mis-numbered array_column.'.format(num_tables_with_issues))
    elif G.VERBOSE:
        indent_debug('Good         : Found no tables with mis-numbered array columns.')
