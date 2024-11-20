# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r451_for_1_table():
    num_findings = 0
    PDS_CRET_TS = False
    PDS_UPDT_TS = False

    for G.COLUMN_ELEMENT in G.TABLE_STRUCTURE.column_elements:

        if check_for_rule_exception(G.RULE_ID,
                                    G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper,
                                    G.COLUMN_ELEMENT.name_upper):
            continue

        column_name = G.COLUMN_ELEMENT.name_upper
        if column_name == 'PDS_CRET_TS':
            PDS_CRET_TS = True
        elif column_name == 'PDS_UPDT_TS':
            PDS_UPDT_TS = True

    if PDS_CRET_TS and (PDS_UPDT_TS is False):
        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='{0}.{1} has the column: PDS_CRET_TS but not the column: PDS_UPDT_TS'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper),
            class_object=G.TABLE_STRUCTURE)

        num_findings += 1

    if num_findings == 1:
        indent_info('Notice       : Table {0}.{1} has the column: PDS_CRET_TS but not the column: PDS_UPDT_TS.'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper))
    elif G.VERBOSE:
        indent_debug('Good         : Table {0}.{1} has no column named PDS_CRET_TS '.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper) +
                     'or has both PDS_CRET_TS and PDS_UPDT_TS.')

    return num_findings


# ===============================================================================
def check_r451():
    '''
    Check that if Redshift column PDS_CRET_TS is used, must also have PDS_UPDT_TS.
    '''

    G.RULE_ID = 'r451'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if G.RULES_ENGINE_TYPE != 'REDSHIFT':
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    tot_num_findings = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID,
                                    G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper):
            continue

        tot_num_findings += check_r451_for_1_table()

    if tot_num_findings > 1:
        indent_info('Notice       : Found {0} tables'.format(tot_num_findings) + \
                    ' with the column: PDS_CRET_TS but not the column: PDS_UPDT_TS.')

    elif tot_num_findings == 1:
        indent_info('Notice       : Found {0} table'.format(tot_num_findings) + \
                    ' with the column: PDS_CRET_TS but not the column: PDS_UPDT_TS.')

    elif G.VERBOSE:
        indent_debug('Good         : No table' + \
                     ' has a column named PDS_CRET_TS or every table has both PDS_CRET_TS and PDS_UPDT_TS.')

    return 0