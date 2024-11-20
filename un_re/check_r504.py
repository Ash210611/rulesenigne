# pylint: disable=C0209           # Don't require formtted strings

import re
import textwrap

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.indent_info import indent_info
from un_re.indent_warning import indent_warning
from un_re.print_msg import report_firm_finding


# ===============================================================================
def dreml_check_nvl():
    """
    This function checks that the sql statement does not use NVL.

    Please use Coalesce instead.

    This function will scan the antlr_log_contents to identify the NVL
    function, because Antlr is the best tool to tokenize the input.
    This will use the input sql_statement to report the context though,
    because that is more human-readable.
    """

    found_it = False

    for line in G.ANTLR_LOG_CONTENTS.split('\n'):
        if re.search(r'\bNVL\b', line, re.IGNORECASE):
            found_it = True
            break

    if found_it:
        report_firm_finding(
            object_type_nm='FILE',
            object_nm=G.SQL_STATEMENT_OBJ.input_filename,
            severity=G.RULES[G.RULE_ID].severity,
            message='Please do not use the NVL function.',
            class_object=G.SQL_STATEMENT_OBJ)

        for line in G.SQL_STATEMENT_OBJ.sql_stmt_txt.split('\n'):
            if re.search(r'\bNVL\b', line, re.IGNORECASE):
                line_fragment = '\n'.join(textwrap.wrap(line, width=80, replace_whitespace=False))
                for line_segment in line_fragment.split('\n'):
                    if re.search(r'\bNVL\b', line_segment, re.IGNORECASE):
                        indent_warning('For example, found this: {0}'.format(line_segment))
                        break
                break

        indent_warning('Please use Coalesce instead of NVL.')

    # elif G.VERBOSE:
    # 	G.LOGGER.debug ((' ' * 15) + 'Good         : The NVL function is not being used.')

    return found_it


# ===============================================================================
def check_r504():
    G.RULE_ID = 'r504'

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

        if dreml_check_nvl():
            num_stmts_w_findings += 1

    if num_stmts_w_findings > 1:
        indent_info(f'Notice       : {num_stmts_w_findings} statements use the NVL function.')

    elif num_stmts_w_findings == 1:
        indent_info('Notice       : 1 statement uses the NVL function.')

    elif G.VERBOSE:
        indent('Good         : No statements use the NVL function.')
