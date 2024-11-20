# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent import indent
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r411_for_1_table():
    if G.TABLE_STRUCTURE.database_base_upper.find('VIEW') > -1:
        found_an_issue = True
    elif G.TABLE_STRUCTURE.database_base_upper.find('VW') > -1:
        found_an_issue = True
    else:
        found_an_issue = False

    if found_an_issue:
        report_adjustable_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='Table {0}.{1} should not be created in a view database.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper),
            adjusted_message='Accepting table {0}.{1} in a view database for ruleset {2}'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.TABLE_STRUCTURE.ruleset),
            class_object=G.TABLE_STRUCTURE)

    if not found_an_issue:
        if G.VERBOSE:
            indent('Good         : Table {0}.{1} is located appropriately.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper))

    return found_an_issue


# ===============================================================================
def check_r411_for_1_view():
    if G.VIEW_STRUCTURE.database_base_upper.find('VIEW') > -1:
        found_an_issue = False
    elif G.VIEW_STRUCTURE.database_base_upper.find('VW') > -1:
        found_an_issue = False
    else:
        found_an_issue = True

    if found_an_issue:
        report_adjustable_finding(
            object_type_nm='VIEW',
            object_nm=G.VIEW_STRUCTURE.view_name_upper,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='View {0}.{1} should not be created in a table database.'.format(
                G.VIEW_STRUCTURE.database_base_upper,
                G.VIEW_STRUCTURE.view_name_upper),
            adjusted_message='Accepting view {0}.{1} in a table database for ruleset {2}'.format(
                G.VIEW_STRUCTURE.database_base_upper,
                G.VIEW_STRUCTURE.view_name_upper,
                G.VIEW_STRUCTURE.ruleset),
            class_object=G.VIEW_STRUCTURE)

    if not found_an_issue:
        if G.VERBOSE:
            indent('Good         : View {0}.{1} is located appropriately.'.format(
                G.VIEW_STRUCTURE.database_base_upper,
                G.VIEW_STRUCTURE.view_name_upper))
    return found_an_issue


# ===============================================================================
def check_r411_for_tables():
    num_table_findings = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if G.TABLE_STRUCTURE.database_base_upper == 'UNKNOWN':
            continue

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        if check_r411_for_1_table():
            num_table_findings += 1

    return num_table_findings


# ===============================================================================
def check_r411_for_views():
    num_view_findings = 0

    for G.VIEW_STRUCTURE in G.VIEW_STRUCTURES:

        if G.VIEW_STRUCTURE.database_base_upper == 'UNKNOWN':
            continue

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.VIEW_STRUCTURE.view_name_upper):
            continue

        if check_r411_for_1_view():
            num_view_findings += 1

    return num_view_findings


# ===============================================================================
def check_r411():
    """
    This rule will check object location.

    Make sure views are in a view database, and tables are in a table
    database.
    """

    G.RULE_ID = 'r411'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if G.RULES_ENGINE_TYPE not in (
            'TERADATA_DDL',
            'REDSHIFT'):
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_findings = 0

    num_findings += check_r411_for_tables()

    num_findings += check_r411_for_views()

    if num_findings == 0:
        if G.VERBOSE:
            indent('Good         : All tables and views are located appropriately.')
