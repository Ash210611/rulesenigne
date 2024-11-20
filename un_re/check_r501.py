# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def dreml_check_in_list_count(antlr_log_contents):
    """
    This function counts the number of items in an IN list.

    It reports a finding if too many are found.
    """

    num_in_values = 0
    num_in_lists_found = 0
    found_long_inlist = False

    for line in antlr_log_contents.split('\n'):
        if re.search('Found IN-list value for      :', line):
            num_in_values += 1
        elif re.search('Finished IN list v2 for      :', line):
            num_in_lists_found += 1
            expression = line.split(':')[1]
            expression = expression.strip()
            if num_in_values >= 20:
                report_firm_finding(
                    object_type_nm='FILE',
                    object_nm=G.SQL_STATEMENT_OBJ.input_filename.replace(G.WORKSPACE + '/', ''),
                    severity=G.RULES[G.RULE_ID].severity,
                    message='A long in-list was found.',
                    class_object=G.SQL_STATEMENT_OBJ)
                found_long_inlist = True
                indent(f'Found {num_in_values} IN-list values')
                indent(f'Found that on the expression for {expression}')

            elif G.VERBOSE:
                indent('Good         : Filename {0} Expression {1} IN-list had {2} (<20) values.'.format(
                    G.SQL_STATEMENT_OBJ.input_filename_rel,
                    expression,
                    num_in_values))

            # Reset the counter in case another IN-list is used
            num_in_values = 0

    return found_long_inlist


# ===============================================================================
def check_r501():
    G.RULE_ID = 'r501'

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

        if dreml_check_in_list_count(G.ANTLR_LOG_CONTENTS):
            num_stmts_w_findings += 1

    if num_stmts_w_findings > 1:
        indent_info('Notice       : {0} statements have long in-lists.'.format(
            num_stmts_w_findings))

    elif num_stmts_w_findings == 1:
        indent_info('Notice       : 1 statement has a long in-list.')

    elif G.VERBOSE:
        indent('Good         : No statements have long in-lists.')

    return
