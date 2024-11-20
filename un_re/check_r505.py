# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G

from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent import indent
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def dreml_check_num_lines():
    found_an_issue = False

    num_lines_found = len(G.SQL_STATEMENT_OBJ.sql_stmt_txt.split('\n'))

    if num_lines_found > 1000:

        report_adjustable_finding(
            object_type_nm='FILE',
            object_nm=G.SQL_STATEMENT_OBJ.input_filename,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='SQL statement has {0} lines (>1000).'.format(num_lines_found),
            adjusted_message=f'Accepting ridiculously long SQL statement for ruleset {G.SQL_STATEMENT_OBJ.ruleset}',
            class_object=G.SQL_STATEMENT_OBJ)

        for preview_line in G.SQL_STATEMENT_OBJ.get_a_little_context():
            indent_info(preview_line)

        indent_info('Please keep the number of lines <= 1000')
        found_an_issue = True

    return found_an_issue


# ===============================================================================
def check_r505():
    G.RULE_ID = 'r505'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_stmts_checked = 0
    num_stmts_w_findings = 0

    for G.SQL_STATEMENT_OBJ in G.SQL_STATEMENT_OBJS:

        if G.SQL_STATEMENT_OBJ.antlr_status != 'SUCCEEDED':
            continue

        num_stmts_checked += 1

        if dreml_check_num_lines():
            num_stmts_w_findings += 1

    if num_stmts_w_findings > 1:
        indent_info('Notice       : {0} statements of {1} exceed 1000 lines.'.format(
            num_stmts_w_findings,
            num_stmts_checked))

    elif num_stmts_w_findings == 1:
        indent_info('Notice       : 1 statement of {0} exceeds 1000 lines.'.format(
            num_stmts_checked))

    elif G.VERBOSE:
        indent('Good         : No statements of {0} exceed 1000 lines.'.format(
            num_stmts_checked))
