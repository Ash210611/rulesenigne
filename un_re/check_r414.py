# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r414_for_1_column():
    if G.COLUMN_ELEMENT.is_identity:
        report_firm_finding(
            object_type_nm='COLUMN',
            object_nm=G.COLUMN_ELEMENT.name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='{0}.{1}.{2} has the IDENTITY datatype'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_ELEMENT.name_upper),
            class_object=G.TABLE_STRUCTURE)
        return True  # There is an issue

    return False  # There is no issue


# ===============================================================================
def check_r414_for_1_table():
    num_findings = 0

    for G.COLUMN_ELEMENT in G.TABLE_STRUCTURE.column_elements:

        if check_for_rule_exception(G.RULE_ID,
                                    G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper,
                                    G.COLUMN_ELEMENT.name_upper):
            continue

        if check_r414_for_1_column():
            num_findings += 1

    if num_findings > 1:
        indent_info('Notice       : Table {0}.{1} has {2} IDENTITY columns.'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper,
            num_findings))

    elif num_findings == 1:
        indent_info('Notice       : Table {0}.{1} has {2} IDENTITY column.'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper,
            num_findings))
    elif G.VERBOSE:
        indent_debug('Good         : Table {0}.{1} has no IDENTITY columns.'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper))

    return num_findings


# ===============================================================================
def check_r414():
    '''
    Check that no IDENTITY datatypes are used
    '''

    G.RULE_ID = 'r414'

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    tot_num_findings = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID,
                                    G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper):
            continue

        tot_num_findings += check_r414_for_1_table()

    if tot_num_findings > 1:
        indent_info('Notice       : Found {0} usages of the IDENTITY datatype.'.format(tot_num_findings))
    elif tot_num_findings == 1:
        indent_info('Notice       : Found {0} usage of the IDENTITY datatype.'.format(tot_num_findings))
    elif G.VERBOSE:
        indent_debug('Good         : No tables use the IDENTITY datatype.')
