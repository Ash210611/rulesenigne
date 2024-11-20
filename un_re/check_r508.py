# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def dreml_check_update_where():
    """
    This function checks that update statements have a where clause.

    We check that UPDATE is not in single quotes by using negative look-
    behind and look-ahead assertions.  We look behind using (?<!').  We
    look ahead using (?!').

    """

    found_an_issue = False

    if not re.search(r"(?<!')\bUPDATE\b(?!')", G.SQL_STATEMENT_OBJ.sql_stmt_txt,
                     re.IGNORECASE | re.MULTILINE):
        # We don't need to check this statement for an update where clause.
        return found_an_issue  # Return False

    if re.search('MERGE', G.SQL_STATEMENT_OBJ.sql_stmt_txt,
                 re.IGNORECASE | re.MULTILINE):
        # We don't need to check this statement for an update where clause.")
        return found_an_issue  # Return False

    found_a_where_clause = False
    for line in G.ANTLR_LOG_CONTENTS.split('\n'):
        if re.search('Found update where clause    : ', line, re.IGNORECASE):
            found_a_where_clause = True
            break

    if not found_a_where_clause:
        found_an_issue = True

        this_object_nm = G.SQL_STATEMENT_OBJ.input_filename.replace(G.WORKSPACE + '/', '') + \
                         ', Stmt: {0}'.format(
                             G.SQL_STATEMENT_OBJ.sql_stmt_num + 1)

        report_adjustable_finding(
            object_type_nm='SQL',
            object_nm=this_object_nm,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='An Update stmt is missing a where clause',
            adjusted_message='Accepting an UPDATE without a WHERE clause in ruleset {0}'.format(
                G.SQL_STATEMENT_OBJ.ruleset),
            class_object=G.SQL_STATEMENT_OBJ)

        for preview_line in G.SQL_STATEMENT_OBJ.get_a_little_context():
            indent_info(preview_line)

    return found_an_issue


# ===============================================================================
def check_r508():
    G.RULE_ID = 'r508'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_stmts_w_findings = 0

    for G.SQL_STATEMENT_OBJ in G.SQL_STATEMENT_OBJS:

        if G.SQL_STATEMENT_OBJ.antlr_status != 'SUCCEEDED':
            continue

        G.ANTLR_LOG_FILENAME = G.SQL_STATEMENT_OBJ.antlr_log_filename

        G.ANTLR_LOG_CONTENTS = get_file_contents(G.ANTLR_LOG_FILENAME)

        if dreml_check_update_where():
            num_stmts_w_findings += 1

    if num_stmts_w_findings > 1:
        indent_info('Notice       : {0} UPDATE statements are missing a WHERE clause.'.format(
            num_stmts_w_findings))

    elif num_stmts_w_findings == 1:
        indent_info('Notice       : 1 UPDATE statement is missing a WHERE clause')

    elif G.VERBOSE:
        indent('Good         : No UPDATE statements are missing a WHERE clause')
