# pylint: disable=C0209			# Don't require formatted strings.

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_g005_for_1_statement(sql_stmt_obj):
    '''
    The tentative_command_type cannot be compared to the actual
    command_type when G.PARALLEL_DEGREE > 1, because the
    tentative_command_type is set in the child process, and is not
    communicated back to the parent.

    Also, we cannot check the command type if the sql_stmt_txt has a
    syntax error.  That condition will be reported by g003.
    '''

    found_issue = False

    if sql_stmt_obj.input_file.has_a_syntax_error:
        return found_issue

    if sql_stmt_obj.antlr_status == 'SKIPPED':
        return found_issue

    message = 'Error: unknown message.'  # Satisfy initialization linting

    if sql_stmt_obj.command_type == 'UNKNOWN':
        found_issue = True
        message = 'Statement {0} command type is unknown.'.format(
            sql_stmt_obj.sql_stmt_num + 1)

    elif G.PARALLEL_DEGREE == 1:
        if sql_stmt_obj.tentative_command_type == 'UNKNOWN':
            found_issue = True
            message = 'Statement {0} tentative command type is unknown.'.format(
                sql_stmt_obj.sql_stmt_num + 1)

        elif sql_stmt_obj.command_type != sql_stmt_obj.tentative_command_type:
            found_issue = True
            message = 'Statement {0} command type differs.'.format(
                sql_stmt_obj.sql_stmt_num + 1)

    if found_issue:
        report_firm_finding(
            object_type_nm='FILE',
            object_nm=sql_stmt_obj.input_file.input_filename_rel,
            severity=G.RULES[G.RULE_ID].severity,
            message=message,
            class_object=sql_stmt_obj.input_file)

        sql_stmt_txt = sql_stmt_obj.sql_stmt_txt.replace('\n', ' ')
        stmt_len = len(sql_stmt_txt)
        if stmt_len >= 34:
            indent_info('SQL Stmt Txt : {0}...'.format(
                sql_stmt_txt[:34]))
        else:
            indent_info('SQL Stmt Txt : {0}'.format(
                sql_stmt_txt[:stmt_len]))

    return found_issue


# ===============================================================================
def check_g005():
    '''
    The UN_RE must be able to classify what kind of command it is reading.
    '''

    G.RULE_ID = 'g005'

    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_found = 0
    for sql_stmt_obj in G.SQL_STATEMENT_OBJS:
        if check_g005_for_1_statement(sql_stmt_obj):
            num_found += 1

    if G.VERBOSE and num_found == 0:
        indent_debug('Good         : All command types are known.')
