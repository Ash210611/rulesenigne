# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r453_for_1_table():
    num_findings = 0
    CRET_TS = False
    UPDT_TS = False
    LOAD_CTL_KEY = False

    for G.COLUMN_ELEMENT in G.TABLE_STRUCTURE.column_elements:

        if check_for_rule_exception(G.RULE_ID,
                                    G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper,
                                    G.COLUMN_ELEMENT.name_upper):
            continue

        column_name = G.COLUMN_ELEMENT.name_upper
        if column_name == 'CRET_TS':
            CRET_TS = True
        elif column_name == 'UPDT_TS':
            UPDT_TS = True
        elif column_name == 'LOAD_CTL_KEY':
            LOAD_CTL_KEY = True

    if not (CRET_TS and UPDT_TS and LOAD_CTL_KEY):
        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='{0}.{1} does not have all these audit columns: CRET_TS, UPDT_TS and LOAD_CTL_KEY'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper),
            class_object=G.TABLE_STRUCTURE)

        num_findings += 1

    if num_findings == 1:
        indent_info('Notice       : ' + \
                    'Table {0}.{1} does not have all these audit columns: CRET_TS, UPDT_TS and LOAD_CTL_KEY.'.format(
                        G.TABLE_STRUCTURE.database_base_upper,
                        G.TABLE_STRUCTURE.table_name_upper))

    elif G.VERBOSE:
        indent_debug(
            'Good         : Table {0}.{1} has all these audit columns: CRET_TS, UPDT_TS and LOAD_CTL_KEY.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper))

    return num_findings


# ===============================================================================
def check_r453():
    '''
    Check that Redshift table should always have these audit columns: CRET_TS, UPDT_TS and LOAD_CTL_KEY.
    '''

    G.RULE_ID = 'r453'

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

        tot_num_findings += check_r453_for_1_table()

    audit_columns = 'CRET_TS, UPDT_TS and LOAD_CTL_KEY'
    if tot_num_findings > 1:
        indent_info('Notice       : Found {0} tables do not have all these audit columns: '.format(
            tot_num_findings) +
                    audit_columns + '.')

    elif tot_num_findings == 1:
        indent_info('Notice       : Found {0} table does not have all these audit columns: {1}.'.format(
            tot_num_findings,
            audit_columns))

    elif G.VERBOSE:
        indent_debug('Good         : Every table has all these audit columns: {0}.'.format(
            audit_columns))

    return 0
