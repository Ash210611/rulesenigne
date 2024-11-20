# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r308_for_1_table():
    found_an_issue = False

    if G.TABLE_STRUCTURE.hive_storage_type.upper() == 'AVRO':
        found_an_issue = True
        report_adjustable_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_NAME,
            normal_severity='WARNING',  # Not Error, or G.RULES[G.RULE_ID].severity
            normal_message='Table storage type was specified as AVRO',
            adjusted_message=f'Accepting AVRO storage type in ruleset {G.TABLE_STRUCTURE.ruleset}',
            class_object=G.TABLE_STRUCTURE)

        indent('It is highly recommended to use PARQUET instead.')
        indent('If AVRO is actually required, please officially request it.')

    elif G.TABLE_STRUCTURE.hive_storage_type.upper() == 'PARQUET':
        if G.VERBOSE:
            indent('Good         : Table {0} uses hive storage type PARQUET.'.format(
                G.TABLE_STRUCTURE.table_name_upper))

    elif G.TABLE_STRUCTURE.hive_storage_type.upper() != '':
        found_an_issue = True
        report_adjustable_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_NAME,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='Table storage type was not specified as PARQUET or AVRO',
            adjusted_message='Accepting odd storage type in ruleset {0}'.format(
                G.TABLE_STRUCTURE.ruleset),
            class_object=G.TABLE_STRUCTURE)

        indent('Found this storage type instead: {0}'.format(
            G.TABLE_STRUCTURE.hive_storage_type))

    elif G.VERBOSE:
        indent('Notice       : Table {0} does not specify a hive storage type.'.format(
            G.TABLE_STRUCTURE.table_name_upper))

    return found_an_issue


# ===============================================================================
def check_r308():
    '''
    Check Hive tables for Parquet or Avro storage
    '''

    G.RULE_ID = 'r308'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if G.RULES_ENGINE_TYPE != 'HIVE_DDL_RE':
        return 0
    # Only Hive has Parquet and Avro storage types

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    # Check the rule now that the prerequisites are passed.
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_tables_with_issues = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_r308_for_1_table():
            num_tables_with_issues += 1

    if num_tables_with_issues == 1:
        indent_info('Notice-{0}  : {1} table is not using an approved storage type'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif num_tables_with_issues > 1:
        indent_info('Notice-{0}  : {1} tables are not using an approved storage type.'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif G.VERBOSE:
        indent_debug('Good         : All tables are using an approved storage type.')

    return 0
