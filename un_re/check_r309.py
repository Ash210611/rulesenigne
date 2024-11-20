# pylint: disable=C0209           		# Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.check_r217 import check_r217_for_1_column
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r309_report_None(dbx_optimize_stmt, zorder_column):
    column_name = zorder_column.column_name

    report_adjustable_finding(
        object_type_nm='COLUMN',
        object_nm=column_name,
        normal_severity=G.RULES[G.RULE_ID].severity,
        normal_message=f'ZORDER column {column_name} classword is: None',
        adjusted_message='Accepting ZORDER column {0} with odd classword in ruleset {1}'.format(
            column_name,
            dbx_optimize_stmt.ruleset),
        class_object=dbx_optimize_stmt)

    if zorder_column.naming_method == 'SNAKE_CASE':
        indent_info('SNAKE_CASE column names should use one of the Physical classwords.')
    elif zorder_column.naming_method == 'MixedCase':
        indent_info('MixedCase column names should use one of the Logical classwords.')
    elif zorder_column.naming_method == 'SMASHED':
        indent_info('SMASHED column names should use one of the Physical or Logical classwords.')


# ===============================================================================
def check_r309_report_DT(dbx_optimize_stmt, zorder_column):
    column_name = zorder_column.column_name

    report_adjustable_finding(
        object_type_nm='COLUMN',
        object_nm=column_name,
        normal_severity=G.RULES[G.RULE_ID].severity,
        normal_message=f'ZORDER column {column_name} has classword {zorder_column.classword}',
        adjusted_message='Accepting ZORDER column {0} with odd classword in ruleset {1}'.format(
            column_name,
            dbx_optimize_stmt.ruleset),
        class_object=dbx_optimize_stmt)

    indent_info('Databricks Optimize Zorder date columns are not recommended.')


# ===============================================================================
def check_r309_for_1_column(dbx_optimize_stmt, zorder_column):
    if zorder_column.classword is None:
        if check_r217_for_1_column(zorder_column.column_name):
            return False  # This column has a classword exception

        check_r309_report_None(dbx_optimize_stmt, zorder_column)
        return True

    if zorder_column.classword in ('DT', 'DATE'):
        check_r309_report_DT(dbx_optimize_stmt, zorder_column)
        return True

    return False


# ===============================================================================
def check_r309_for_1_stmt(dbx_optimize_stmt):
    found_an_issue = False

    # print (dbx_optimize_stmt)
    for zorder_column in dbx_optimize_stmt.zorder_columns:
        # print (zorder_column)

        if check_r309_for_1_column(dbx_optimize_stmt, zorder_column):
            found_an_issue = True

    return found_an_issue


# ===============================================================================
def check_r309():
    '''
    r309   | TABLE          | Databricks Optimize ZORDER columns should not be dates.
    '''

    G.RULE_ID = 'r309'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if G.RULES_ENGINE_TYPE != 'DATABRICKS':
        return
    # Only Hive has Parquet and Avro storage types

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    if len(G.DBX_OPTIMIZE_STMTS) == 0:
        return

    # -----------------------------------------------------------------------
    # Check the rule now that the prerequisites are passed.
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_stmts_with_issues = 0

    for dbx_optimize_stmt in G.DBX_OPTIMIZE_STMTS:

        if check_r309_for_1_stmt(dbx_optimize_stmt):
            num_stmts_with_issues += 1

    if num_stmts_with_issues == 1:
        indent_info('Notice-{0}  : {1} optimize statement has a zorder column issue.'.format(
            G.RULE_ID,
            num_stmts_with_issues))
    elif num_stmts_with_issues > 1:
        indent_info('Notice-{0}  : {1} optimize statements have a zorder column issue.'.format(
            G.RULE_ID,
            num_stmts_with_issues))
    elif G.VERBOSE:
        indent_debug('Good         : No optimize statements have a zorder column issue.')

    return
