# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent import indent
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding
from un_re.split_name_parts import split_name_parts
from un_re.split_value_from_line import split_value_from_line


# ==============================================================================
def backup_table_extension_is_good(table_a, table_b):
    _, table_name_tokens = split_name_parts('TABLE', table_a, 'UNKNOWN')

    if table_name_tokens[-1] not in ('BAK', 'MVC_BAK'):
        indent_info('Notice-{0}  : It does not appear the backup table suffix is _BAK.'.format(
            G.RULE_ID))
        indent('Please use the _BAK extension.')
        indent_info('TABLE_A      = ' + table_a)
        indent_info('TABLE_B      = ' + table_b)
        return False

    tablename_diff = table_a.replace(table_b, '', 1)
    if tablename_diff not in ('_BAK', '_MVC_BAK'):
        indent_info('Notice-{0}  : It does not appear the backup table is named for the source table.'.format(
            G.RULE_ID))
        indent_info('TABLE_A      = ' + table_a)
        indent_info('TABLE_B      = ' + table_b)
        return False

    return True


# ===============================================================================
# noinspection PyInconsistentIndentation
def check_r408_for_1_stmt():
    found_issue = False
    table_a = 'Something'
    table_b = 'Error'

    for line in G.SQL_STATEMENT_OBJ.antlr_log_contents.split('\n'):
        if re.search(r'Found table name             : ', line, re.IGNORECASE):
            table_a = split_value_from_line(line)
        if re.search(r'  Source Table               : ', line, re.IGNORECASE):
            table_b = split_value_from_line(line)

    if not backup_table_extension_is_good(table_a, table_b):
        found_issue = True

        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=table_b,
            severity=G.RULES[G.RULE_ID].severity,
            message="Backup Table name {0} doesn't correspond.".format(table_a),
            class_object=G.SQL_STATEMENT_OBJ)
        G.LOGGER.info('')

    elif G.VERBOSE:
        indent('Good         : File {0}, Stmt {1} Backup Tablename = {2}.'.format(
            G.SQL_STATEMENT_OBJ.input_filename.replace(G.WORKSPACE + '/', ''),
            G.SQL_STATEMENT_OBJ.sql_stmt_num + 1,
            table_a))

    return found_issue


# ===============================================================================
def check_r408():
    """
    Search Insert statements for Select-Star.
    There may be more than 1 space between Select and Star
    Do not lump Select Count(*) with Select-Star
    """

    G.RULE_ID = 'r408'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if G.RULES_ENGINE_TYPE != 'TERADATA_DDL':
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_checked = 0
    num_findings = 0
    for G.SQL_STATEMENT_OBJ in G.SQL_STATEMENT_OBJS:

        if G.SQL_STATEMENT_OBJ.command_type != "BACKUP TABLE":
            continue

        num_checked += 1

        if check_r408_for_1_stmt():
            num_findings += 1

    if num_checked == 0:
        if G.VERBOSE:
            indent('Notice       : No Backup Table commands are found.')
    elif num_findings == 0:
        if G.VERBOSE:
            indent('Good         : All Backup Table commands use the right suffix.')
    else:
        # At this point, num_checked and num_findings > 0
        if num_findings == 1:
            indent('Notice       : 1 Backup Table is misnamed.')

        elif num_findings > 1:
            indent('Notice       : {0} Backup Tables of {1} are misnamed.'.format(
                num_findings,
                num_checked))

    return
