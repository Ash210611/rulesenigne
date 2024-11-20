# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G

from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def is_r004_checkable_for_this_column():
    if G.COLUMN_ELEMENT.datatype is None:
        return False
    # This can happen for example from a DDL file that only
    # has COMMENT ON commands, not actually creating a column

    if G.COLUMN_ELEMENT.column_name_tokens[0].upper() == 'SRC':
        G.COLUMN_ELEMENT.classword = ''
        if G.VERBOSE:
            indent_debug('Notice       : {0}.{1}.{2} skipping {3} for a SRC column'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_NAME,
                G.RULE_ID))
        return False  # Don't check classwords and datatypes for SRC columns

    if G.COLUMN_ELEMENT.column_name_tokens[0].upper() == 'DEXL':
        G.COLUMN_ELEMENT.classword = ''
        if G.VERBOSE:
            indent_debug('Notice       : {0}.{1}.{2} skipping {3} for a DEXL column'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_NAME,
                G.RULE_ID))
        return False  # Don't check classwords and datatypes for DEXL columns

    return True  # It is checkable.


# ===============================================================================
def check_datatype_for_classword_for_one_column(classword_to_check):
    G.COLUMN_NAME = G.COLUMN_ELEMENT.name_upper

    if not is_r004_checkable_for_this_column():
        return False  # meaning this is not an issue

    found_match = False
    if classword_to_check == G.COLUMN_ELEMENT.classword:

        for allowed_datatype in G.CLASSWORD_DATATYPES[classword_to_check].allowed_datatypes:
            if allowed_datatype.size is None:
                # Then only compare the datatype, not the size
                if G.COLUMN_ELEMENT.datatype == allowed_datatype.datatype:
                    found_match = True
                    break
            else:
                if G.COLUMN_ELEMENT.datatype_w_size == allowed_datatype.datatype_w_size:
                    found_match = True
                    break

    if not found_match:
        # Check if it is on the list of approved variations

        for variation in G.CLASSWORD_DATATYPE_VARIATIONS:
            if variation.classword != classword_to_check:
                continue

            if variation.column_nm != G.COLUMN_ELEMENT.name_upper:
                continue

            if variation.datatype_w_size != G.COLUMN_ELEMENT.datatype_w_size:
                indent_info('Notice       : Column name {0}.{1}.{2} is not a {3}.'.format(
                    G.TABLE_STRUCTURE.database_base_upper,
                    G.TABLE_STRUCTURE.table_name_upper,
                    G.COLUMN_ELEMENT.name_upper,
                    variation.datatype_w_size))
                continue

            indent_info('Notice       : Column name {0}.{1}.{2} is approved as a {3}.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_ELEMENT.name_upper,
                variation.datatype_w_size))
            return False

    if not found_match:
        this_object_name = '{0}.{1}.{2}'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper,
            G.COLUMN_NAME)

        report_adjustable_finding(
            object_type_nm='COLUMN NAME',
            object_nm=this_object_name,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='Column {0} using classword {1}, has a non-standard datatype.'.format(
                this_object_name,
                classword_to_check),
            adjusted_message='Accepting non-standard datatype for {0} as a {1}'.format(
                this_object_name,
                G.COLUMN_ELEMENT.datatype_w_size),
            class_object=G.TABLE_STRUCTURE)
        indent_info((' ' * 15) + 'It has a {0} datatype, while the expected datatypes are {1}'.format(
            G.COLUMN_ELEMENT.datatype_w_size,
            G.CLASSWORD_DATATYPES[classword_to_check].allowed_datatypes))

    return not found_match


# will return false if no classword - datatype mismatch is found
# will return true if a classword - dataype mismatch is found

# ===============================================================================
def check_datatype_for_classword_for_1_table(classword_to_check):
    num_columns_with_issues = 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
        return num_columns_with_issues  # return 0

    if G.TABLE_STRUCTURE.table_name_tokens[0].upper() in ('W', 'TEMP', 'TMP'):

        # Skip this rule for work tables.
        if G.VERBOSE:
            indent_debug('Notice-{0}  : Skipping {0} for a Work table: {1}.'.format(
                G.RULE_ID,
                G.TABLE_STRUCTURE.table_name_upper))
        return num_columns_with_issues  # return 0

    if len(G.TABLE_STRUCTURE.column_elements) == 0:
        indent_debug('Good         : {0} has no columns to check.'.format(
            G.TABLE_STRUCTURE.table_name_upper))
        return num_columns_with_issues

    G.COLUMN_ELEMENTS = G.TABLE_STRUCTURE.column_elements

    num_columns_with_that_classword = 0
    for G.COLUMN_ELEMENT in G.COLUMN_ELEMENTS:

        if classword_to_check != G.COLUMN_ELEMENT.classword:
            continue
        num_columns_with_that_classword += 1

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper,
                                    G.COLUMN_ELEMENT.name_upper):
            continue

        if check_datatype_for_classword_for_one_column(classword_to_check):
            num_columns_with_issues += 1

    if num_columns_with_that_classword > 0 and num_columns_with_issues == 0:
        if G.VERBOSE:
            indent_debug(
                'Good         : All columns in {0} with classword {1} are using an appropriate datatype.'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    classword_to_check))

    return num_columns_with_issues


# ===============================================================================
def check_one_classword(classword_to_check):
    # -----------------------------------------------------------------------
    # See if there are any columns for this datatype

    at_least_one_table_has_this_classword = False
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:
        for G.COLUMN_ELEMENT in G.TABLE_STRUCTURE.column_elements:
            if classword_to_check == G.COLUMN_ELEMENT.classword:
                at_least_one_table_has_this_classword = True
                break
        if at_least_one_table_has_this_classword:
            break

    if not at_least_one_table_has_this_classword:
        return

    # -----------------------------------------------------------------------

    num_tables_with_issues = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_datatype_for_classword_for_1_table(classword_to_check) > 0:
            num_tables_with_issues += 1

    if num_tables_with_issues == 1:
        indent_info('Notice-{0}  : 1 table has one or more columns '.format(
            G.RULE_ID) + \
                    'where a {0} classword does not have an appropriate datatype.'.format(
                        classword_to_check))
    elif num_tables_with_issues > 1:
        indent_info('Notice-{0}  : {1} tables have one or more columns '.format(
            G.RULE_ID,
            num_tables_with_issues) + \
                    'where a {0} classword does not have an appropriate datatype.'.format(
                        classword_to_check))
    elif G.VERBOSE:
        indent_debug('Good         : All tables with a {0} column name are using '.format(classword_to_check) + \
                     'an appropriate datatype for it.')


# ===============================================================================
def check_r004():
    """
    Checks that a particular classword has a specific datatype.
    """

    G.RULE_ID = 'r004'

    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    # -----------------------------------------------------------------------
    # Check prerequisites

    if G.RULE_ID not in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    for classword_to_check in G.PHYSICAL_CLASSWORD_LIST:
        check_one_classword(classword_to_check)
