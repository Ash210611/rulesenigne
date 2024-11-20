# pylint: disable=R0912				# Too many branches
# pylint: disable=R0915				# Too many statements

# ==============================================================================
import sys

from typing import List

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G


# ===============================================================================
def merge_compound_mixed_parts(part_list: List[str]):
    '''
    Merge specified tokens that should be recognized as compound names

    For example,
        Input	: ['Report', 'Year', 'Month']
        Output	: ['Report', 'YearMonth']

    For example,
        Input	: ['Account', 'Experience', 'Beginning', 'Year', 'Month']
        Output	: ['Account', 'Experience', 'Beginning', 'YearMonth']
    '''

    new_part_list = []
    num_parts = len(part_list)

    n = 0
    while n < num_parts:
        if part_list[n] == 'Year':
            if n < num_parts - 1:
                if part_list[n + 1] == 'Month':
                    new_part_list.append('YearMonth')
                    # Skip this token
                    n += 1
                else:
                    new_part_list.append('Year')
            else:
                new_part_list.append('Year')
        else:
            new_part_list.append(part_list[n])
        n += 1

    return new_part_list


# ===============================================================================
def merge_compound_snake_parts(part_list: List[str]):
    '''
    Merge specified tokens that should be recognized as compound names

    For example,
        Input	: ['RPT', 'YR', 'MTH']
        Output	: ['RPT', 'YR_MTH']

    For example,
        Input	: ['ACCT', 'EXPER', 'BEG', 'YR', 'MTH']
        Output	: ['ACCT', 'EXPER', 'BEG', 'YR_MTH']
    '''

    new_part_list = []
    num_parts = len(part_list)

    n = 0
    while n < num_parts:

        if part_list[n] == 'YR':
            if n < num_parts - 1:
                if part_list[n + 1] == 'MTH':
                    # Skip this token
                    new_part_list.append('YR_MTH')
                    n += 1
                else:
                    new_part_list.append('YR')
            else:
                new_part_list.append('YR')
        else:
            new_part_list.append(part_list[n])

        n += 1

    return new_part_list


# ===============================================================================
def snake_case_parts(input_name):
    part_list = input_name.split('_')

    # Capitalize each token in the part list
    part_list = [x.upper() for x in part_list]

    part_list = merge_compound_snake_parts(part_list)

    naming_method = 'SNAKE_CASE'

    return naming_method, part_list


# ===============================================================================
def is_mixed_case(input_name):
    upper_case_found = False
    lower_case_found = False
    for ch in input_name:
        if ch.isupper():
            upper_case_found = True
        elif ch.islower():
            lower_case_found = True

        if upper_case_found and lower_case_found:
            return True

    return False


# ===============================================================================
def split_mixed_case(input_name, table_naming_method, source):
    """
    To handle capitalized abbreviations, this algorithm makes two passes.

    Suppose the input name = 'LoadFDACtlKey'

    The first pass will produce this list:
        ['Load', 'F', 'D', 'A', 'Ctl', 'Key']
    The second pass coalesces consecutive capitals into the abbreviation
        ['Load', 'FDA', 'Ctl', 'Key']

    Digits are coalesced like capitals are.

    While nobody wants to make more passes than necessary, the advantage of
    two passes is that we can check list elements ahead (n+1)
    """

    # ----------------------------------------------------------------------
    # Mixed Case Pass #1
    # Initialize some variables used inside the loop
    temp_list = []
    current_part = ''

    for ch in input_name:
        if ch.isupper() or ch.isdigit():
            if current_part:
                temp_list.append(current_part)
            current_part = ch
        elif ch.islower():
            current_part += ch

    # Remember to append the last part
    temp_list.append(current_part)

    # ----------------------------------------------------------------------
    # Mixed Case Pass #2, coalesce consecutive capitals or digits
    temp_len = len(temp_list)
    part_list = []
    current_abbreviation = ''

    # print ('temp_len = {0}'.format (temp_len))

    for n in range(temp_len):
        this_word = temp_list[n]
        # print ('n = {0}, this_word = {1}'.format (n, this_word))

        if len(this_word) > 1:
            part_list.append(this_word)

        else:
            # if here, len (this_word) == 1

            if current_abbreviation == '':
                current_abbreviation += this_word

            if n == temp_len - 1:
                # We are at the end of the temp list.
                # Append the current abbreviation.
                part_list.append(current_abbreviation)
                current_abbreviation = ''

            else:
                # It is safe to check n+1
                if len(temp_list[n + 1]) > 1:
                    # This is the end of the current abbreviation
                    part_list.append(current_abbreviation)
                    current_abbreviation = ''
                else:
                    current_abbreviation += temp_list[n + 1]

    # print ('n = {0}, part_list = {1}'.format (n, part_list))

    if input_name == 'Something':
        # The token 'Something' is not an actual name.
        # That is substituted for variable references.
        if source == 'TABLE':
            naming_method = 'MixedCase'
        else:
            # source == 'COLUMN'
            naming_method = table_naming_method

    else:
        naming_method = 'MixedCase'

    part_list = merge_compound_mixed_parts(part_list)

    return naming_method, part_list


# ===============================================================================
def split_smashed_case(input_name, table_naming_method):
    """
    source = 'COLUMN'

    The global classword lists are all in uppercase.
    """

    part_list = []
    for classword in G.PHYSICAL_CLASSWORD_LIST:
        if input_name == classword:
            # Like if the column name == "ID" by itself.
            return table_naming_method, [input_name]

        if input_name.endswith(classword):
            part_list = [input_name[:-len(classword)], classword]
            return 'SMASHED', part_list

    for classword in G.LOGICAL_CLASSWORD_LIST:
        if input_name == classword:
            # Like if the column name == "NAME" by itself.
            return table_naming_method, [input_name]

        if input_name.endswith(classword):
            part_list = [input_name[:-len(classword)], classword]
            return 'SMASHED', part_list

    return table_naming_method, [input_name]


# ===============================================================================
def split_table_parts(input_name, table_naming_method):
    """
    A table name cannot have a datatype suffix, so it is not possible to
    recognize the SMASHED naming method for a table name.

    If there is an underscore, then the naming method == SNAKE_CASE.

    Else if there is variation in the capitalization, then the
        naming_method == 'MIXED_CASE'

    Else it is SNAKE_CASE.   For example if the table_name == 'ADDR', there
        is no underscore, but there is no change in capitalization
        either, so we have to guess that it is SNAKE_CASE.
    """

    if input_name.find('_') > -1:
        return snake_case_parts(input_name)

    if is_mixed_case(input_name):
        return split_mixed_case(input_name, table_naming_method, source='TABLE')

    # Else
    # If there are no variations in capitalization
    # such as for a one-word name, like ADDR or VENDR
    return 'SNAKE_CASE', [input_name]


# ===============================================================================
def split_column_parts(input_name, table_naming_method):
    if input_name.find('_') > -1:
        naming_method, part_list = snake_case_parts(input_name)
        return naming_method, part_list

    if is_mixed_case(input_name):
        return split_mixed_case(input_name, table_naming_method, source='COLUMN')

    return split_smashed_case(input_name.upper(), table_naming_method)


# ===============================================================================
def split_name_parts(
        source: str,
        input_name: str,
        table_naming_method: str):
    """
    Valid values for the source are either TABLE or COLUMN.  That value
    is used for reporting when the name cannot be split.

    This module will check if the input_name has an underscore.

    If it does, it will split the parts using the underscore, and return.

    Otherwise, it will check if the name is Mixed Case.
    If it is, it will split the parts using Mixed Case rules.

    For columns, every column name should have a classword.
    The classword should be delimited with an underscore for SNAKE_CASE.
    Or it could be delimited with a change in capitalization for MixedCase.
    Or it might be SMASHED if the end of the column name is a classword.

    Inconsistencies in the naming method will be checked and reported later
    by the check_g011 function. The finding cannot be reported in this
    function because this split_name_part function is called by the
    constructor.  So the class object is still being constructed, and we
    don't yet have all the attributes set for reporting findings.
    """

    if source == 'TABLE':
        return split_table_parts(input_name, table_naming_method)

    if source == 'COLUMN':
        return split_column_parts(input_name, table_naming_method)

    print('ERROR: Invalid source type in split_name_parts.')
    sys.exit(E.INVALID_SOURCE_NAME)
