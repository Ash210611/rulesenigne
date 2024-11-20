# import    sys

import un_re.global_shared_vars as G

from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r1001_for_1_table():
    found_issue = False
    if G.TABLE_STRUCTURE.command_type != 'CREATE TABLE' and \
            G.TABLE_STRUCTURE.command_type != 'CREATE TABLE AS SELECT':
        # print ('This is not a Create Table statement')
        return found_issue
    if G.TABLE_STRUCTURE.num_collect_stats > 1:
        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_NAME,
            severity=G.RULES[G.RULE_ID].severity,
            message='{0}.{1} has {2} COLLECT STATS (or) STATISTICS commands.Expected 1 collect stats only.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.TABLE_STRUCTURE.num_collect_stats),
            class_object=G.TABLE_STRUCTURE)
        found_issue = True
    elif G.TABLE_STRUCTURE.num_collect_stats == 1:
        indent_info('*' * 100)
        indent_info('Good         : Table {0}.{1} only has {2} COLLECT STATS (or) STATISTICS command.'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper,
            G.TABLE_STRUCTURE.num_collect_stats))
        indent_info('*' * 100)
    elif G.TABLE_STRUCTURE.num_collect_stats == 0:
        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_NAME,
            severity=G.RULES[G.RULE_ID].severity,
            message='{0}.{1} has {2} COLLECT STATS (or) STATISTICS commands.Expected atleast 1 collect stats.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.TABLE_STRUCTURE.num_collect_stats),
            class_object=G.TABLE_STRUCTURE)
        found_issue = True
    elif G.VERBOSE:
        indent_info('*' * 100)
        indent_info('Info         : Table {0}.{1} only has {2} COLLECT STATS (or) STATISTICS command.'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper,
            G.TABLE_STRUCTURE.num_collect_stats))
        indent_info('*' * 100)

    return found_issue


# ===============================================================================
def check_r1001():
    G.RULE_ID = 'r1001'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    if G.RULES_ENGINE_TYPE != 'TERADATA_DDL':
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    G.LOGGER.info('=' * 100)

    num_findings = 0

    indent_info('Total Tables       : {0}'.format(len(G.TABLE_STRUCTURES)))
    indent_info('TABLE STRUCTURES       : {0}'.format(G.TABLE_STRUCTURES))

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        indent_info('Starting validation for TABLE NAME       : {0}'.format(G.TABLE_STRUCTURE.table_name_upper))
        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            return 0

        if check_r1001_for_1_table():
            num_findings += 1

    if num_findings > 1:
        # print ('*' * 120)
        indent_info('Notice       : {0} tables have some unexpected content.'.format(num_findings))
        indent_info('*' * 100)
    elif num_findings == 1:
        # print ('*' * 100)
        indent_info('Notice       : {0} table has some unexpected content.'.format(num_findings))
        indent_info('*' * 100)
    elif G.VERBOSE:
        indent_info('*' * 100)
        indent_info('Good         : No tables had any unexpected content.')
        indent_info('*' * 100)

    G.LOGGER.info('=' * 100)

    return 0
