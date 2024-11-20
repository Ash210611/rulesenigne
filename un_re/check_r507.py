# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def dreml_check_select_star():
    found_an_issue = False

    for line in G.ANTLR_LOG_CONTENTS.split('\n'):
        if not re.search(': ', line):
            continue

        line = line.strip()
        if re.search('Projecting                   : ASTERISK', line):

            this_object_nm = G.SQL_STATEMENT_OBJ.input_filename.replace(G.WORKSPACE + '/', '') + \
                             ', Stmt: {0}'.format(
                                 G.SQL_STATEMENT_OBJ.sql_stmt_num + 1)

            report_adjustable_finding(
                object_type_nm='SQL',
                object_nm=this_object_nm,
                normal_severity=G.RULES[G.RULE_ID].severity,
                normal_message='Projecting Asterisk.  Must avoid specifying Select *.',
                adjusted_message='Accepting Select * in ruleset {0}'.format(
                    G.SQL_STATEMENT_OBJ.ruleset),
                class_object=G.SQL_STATEMENT_OBJ)

            for preview_line in G.SQL_STATEMENT_OBJ.get_a_little_context():
                indent_info(preview_line)

            found_an_issue = True
            break

    return found_an_issue


# ===============================================================================
def check_r507():
    G.RULE_ID = 'r507'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_stmts_w_findings = 0

    for G.SQL_STATEMENT_OBJ in G.SQL_STATEMENT_OBJS:

        G.ANTLR_LOG_FILENAME = G.SQL_STATEMENT_OBJ.antlr_log_filename

        G.ANTLR_LOG_CONTENTS = get_file_contents(G.ANTLR_LOG_FILENAME)

        if dreml_check_select_star():
            num_stmts_w_findings += 1

    num_stmts = len(G.SQL_STATEMENT_OBJS)
    if num_stmts_w_findings > 1:
        indent_info('Notice       : {0} statements of {1} are using Select *.'.format(
            num_stmts_w_findings,
            num_stmts))

    elif num_stmts_w_findings == 1:
        indent_info('Notice       : 1 statement of {0} is using Select *.'.format(
            num_stmts))

    elif G.VERBOSE:
        indent('Good         : No statements of {0} are using Select *.'.format(
            num_stmts))
