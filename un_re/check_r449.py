# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r449_for_1_table():
    num_findings = 0
    not_found_distkey_column = True

    if G.REDSHIFT_TABLE_STRUCTURE.command_type == 'CREATE TABLE AS SELECT':
        return num_findings

    if not G.REDSHIFT_TABLE_STRUCTURE.distkey:
        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=G.REDSHIFT_TABLE_STRUCTURE.table_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='{0}.{1} does not have a distkey'.format(
                G.REDSHIFT_TABLE_STRUCTURE.database_base_upper,
                G.REDSHIFT_TABLE_STRUCTURE.table_name_upper),
            class_object=G.REDSHIFT_TABLE_STRUCTURE)

        num_findings += 1
    else:
        for G.COLUMN_ELEMENT in G.REDSHIFT_TABLE_STRUCTURE.column_elements:

            if check_for_rule_exception(G.RULE_ID,
                                        G.PROJECT_NAME,
                                        G.REDSHIFT_TABLE_STRUCTURE.table_name_upper,
                                        G.COLUMN_ELEMENT.name_upper):
                continue

            if G.REDSHIFT_TABLE_STRUCTURE.distkey_column != 'UNKNOWN' or G.REDSHIFT_TABLE_STRUCTURE.distkey_column == 'DEFAULT':
                if G.REDSHIFT_TABLE_STRUCTURE.distkey_column == 'DEFAULT':
                    not_found_distkey_column = False
                elif G.COLUMN_ELEMENT.name_upper == G.REDSHIFT_TABLE_STRUCTURE.distkey_column:
                    not_found_distkey_column = False

        if not_found_distkey_column:
            report_firm_finding(
                object_type_nm='TABLE',
                object_nm=G.REDSHIFT_TABLE_STRUCTURE.table_name_upper,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0}.{1} does not have a proper distkey. {2} is not a valid column'.format(
                    G.REDSHIFT_TABLE_STRUCTURE.database_base_upper,
                    G.REDSHIFT_TABLE_STRUCTURE.table_name_upper,
                    G.REDSHIFT_TABLE_STRUCTURE.distkey_column),
                class_object=G.REDSHIFT_TABLE_STRUCTURES)

            num_findings += 1

    return num_findings


# ===============================================================================
def check_r449():
    '''
    Check that all tables have distribution key i.e. distkey
    '''

    G.RULE_ID = 'r449'

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

    for G.REDSHIFT_TABLE_STRUCTURE in G.REDSHIFT_TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID,
                                    G.PROJECT_NAME,
                                    G.REDSHIFT_TABLE_STRUCTURE.table_name_upper):
            continue

        tot_num_findings += check_r449_for_1_table()

    if tot_num_findings > 1:
        indent_info('Notice       : Found {0} tables without a distkey.'.format(tot_num_findings))
    elif tot_num_findings == 1:
        indent_info('Notice       : Found {0} table without a distkey.'.format(tot_num_findings))
    elif G.VERBOSE:
        indent_debug('Good         : Every table has a distkey.')

    return 0
