# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ======== ========= ========= ========= ========= ========= ========= ==========
def check_r405_for_1_table():
    found_issue = False

    if G.TABLE_STRUCTURE.num_collect_stats > 1:

        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_NAME,
            severity=G.RULES[G.RULE_ID].severity,
            message='{0}.{1} has {2} COLLECT STATS commands.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.TABLE_STRUCTURE.num_collect_stats),
            class_object=G.TABLE_STRUCTURE)

        found_issue = True

    elif G.VERBOSE:
        if G.TABLE_STRUCTURE.num_collect_stats == 0:
            indent_debug('Notice       : Table {0}.{1} has {2} COLLECT STATS commands.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.TABLE_STRUCTURE.num_collect_stats))
        else:
            indent_debug('Good         : Table {0}.{1} only has {2} COLLECT STATS command.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.TABLE_STRUCTURE.num_collect_stats))

    return found_issue


# ======== ========= ========= ========= ========= ========= ========= ==========
def check_r405():
    """
    Check all the split files.
    If we find another split file that says to COLLECT STATS
    on same COLLECT_TABLE as this one, those should be consolidated.
    """

    G.RULE_ID = 'r405'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    total_num_findings = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        if check_r405_for_1_table():
            total_num_findings += 1

    if total_num_findings > 1:
        indent_info('Notice       : {0} tables were missing some expected content.'.format(total_num_findings))

    elif total_num_findings == 1:
        indent_info('Notice       : {0} table was missing some expected content.'.format(total_num_findings))

    elif G.VERBOSE:
        indent('Good         : No tables have multiple COLLECT STATS commands.')

    return
