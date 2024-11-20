# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.indent_info import indent_info
from un_re.indent_warning import indent_warning
from un_re.print_msg import report_firm_finding


# ===============================================================================
def dreml_check_cross_join():
    """
    The way this works is:
    - Read the Antlr log filename, one line at a time.
    - Raise a warning if you see a line indicate a Cross Join was used.
    """

    found_one = False

    if G.SQL_STATEMENT_OBJ.command_type not in ('SELECT', 'INSERT',
                                                'UPDATE', 'DELETE', 'CREATE VIEW', 'CREATE TABLE AS SELECT'):
        return found_one

    relation_source = ''

    for line in G.ANTLR_LOG_CONTENTS.split('\n'):
        if not re.search(': ', line):
            continue

        if re.search('Found relation source        :', line):

            relation_source = line.split(':')[1]
            relation_source = relation_source.strip()

        elif re.search('Found join type              : CROSS JOIN', line):

            report_firm_finding(
                object_type_nm='FILE',
                object_nm=G.SQL_STATEMENT_OBJ.input_filename,
                severity=G.RULES[G.RULE_ID].severity,
                message='Found Cross Join.',
                class_object=G.SQL_STATEMENT_OBJ)

            indent_warning((' ' * 15) + f'near relation source: {relation_source}')
            found_one = True

    return found_one


# ===============================================================================
def check_r500():
    G.RULE_ID = 'r500'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_stmts_w_findings = 0

    for G.SQL_STATEMENT_OBJ in G.SQL_STATEMENT_OBJS:

        if G.SQL_STATEMENT_OBJ.antlr_status != 'SUCCEEDED':
            continue

        G.ANTLR_LOG_FILENAME = G.SQL_STATEMENT_OBJ.antlr_log_filename

        G.ANTLR_LOG_CONTENTS = get_file_contents(G.ANTLR_LOG_FILENAME)

        if dreml_check_cross_join():
            num_stmts_w_findings += 1

    if num_stmts_w_findings > 1:
        indent_info('Notice       : {0} statements have cross joins.'.format(
            num_stmts_w_findings))

    elif num_stmts_w_findings == 1:
        indent_info('Notice       : 1 statement has a cross join.')

    elif G.VERBOSE:
        indent('Good         : No statements have a cross join.')
