# pylint: disable=C0209           # Don't require formtted strings

import os  # for path.exists
import re  # for search
import subprocess  # for call
import sys  # for exit

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G
from un_re.antlr_show_context import antlr_show_context
from un_re.fprint import fprint
from un_re.get_file_contents import get_file_contents
from un_re.indent_warning import indent_warning
from un_re.print_msg import print_msg


# ===============================================================================
def antlr_parse_stmt_check_for_issues():
    issue_dict = {16: 'no viable alternative',
                  # for example: line 120:39 no viable alternative at input '(alignment_cd=...
                  17: 'extraneous input ',
                  # for example, line 20:28 extraneous input ',' expecting {'SYS_CALENDAR.CALENDAR', INTEGER_VALUE,...
                  18: 'mismatched input ',
                  # for example, line 13:14 mismatched input ')' expecting {CASE_N, COLUMN, RANGE_N}
                  19: r'^line.*:.*missing.*at',
                  # for example: line 2:6 missing {T_GO, ';'} at 'IF'
                  20: 'token recognition error'
                  # for example: line 1:26 token recognition error at: '~'
                  }

    for log_line in G.ANTLR_LOG_CONTENTS.split('\n'):

        for error_num, search_string in issue_dict.items():

            if re.search(search_string, log_line):
                return error_num, log_line

    return 0, ''


# ===============================================================================
def report_antlr_issue_parsing_stmt(filename_to_check, ret, log_line):
    G.RULE_ID = 'g003'

    # It will be reported informally here, to start with.
    # It will be reported with the severity specific to the
    # RULES_ENGINE_TYPE as part of the check_g003 function,
    # which will also check if the project has an exception.

    # use print_and_log?

    for file_obj in G.INPUT_FILES:
        if file_obj.input_filename_rel == G.INPUT_FILENAME_REL:
            # Mark it now to be reported later by the
            # check_g003 function.
            file_obj.has_a_syntax_error = True
            break

    msg = '{0}-{1}   : Unknown syntax errors were found.   Please check that.'.format(
        G.RULES[G.RULE_ID].severity,
        G.RULE_ID)

    print_msg(msg)

    indent_warning(f'Failed to check this statement with Antlr. RET = {ret}')

    antlr_show_context(log_line, filename_to_check)

    failed_log_filename = filename_to_check + '.failed.antlr.re.log'
    os.rename(G.ANTLR_LOG_FILENAME, failed_log_filename)
    G.ANTLR_LOG_FILENAME = failed_log_filename


# ===============================================================================
def antlr_parse_stmt(grammar, filename_to_check):
    '''
    The Antlr function checks syntax of SQL and DDL commands in the
    the LOCAL_SCRIPT_NAME, which is the local copy of the original source
    file for a single statement.

    The antlr_full_contents will contain the complete output from Antlr.
    The ANTLR_LOG_FILENAME will only contain the output from Antlr actions.
    The tokens_log_filename will only contain the tokens from the lexer.

    The antlr_full_contents = tokens_log_filename + G.ANTLR_LOG_FILENAME
    '''

    G.ANTLR_LOG_FILENAME = filename_to_check + '.antlr.re.log'
    antlr_full_contents = filename_to_check + '.antlr_full.re.log'

    grun = 'java org.antlr.v4.gui.TestRig'

    os_command = '{0} {1} root -tokens < {2} > {3} 2>&1'.format(
        grun,
        grammar,
        filename_to_check,
        antlr_full_contents)

    sys.stdout.flush()  # Always flush the console log
    # output before calling a system function.

    G.ANTLR_LOG_CONTENTS = ''

    # -----------------------------------------------------------------------
    try:
        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error('Child was terminated by signal {0}'.format(-ret))
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

    except OSError as e:
        G.LOGGER.error('Antlr execution failed: {0}'.format(e))
        sys.exit(E.ANTLR_EXECUTION_FAILED)

    # -----------------------------------------------------------------------
    # If here, ret >= 0
    # Split the full contents into separate files for the tokens and the
    # action outputs.   The tokens can sometimes useful for diagnostics,
    # but it is inefficient for the rules engine to skip past them repeatedly.

    if not os.path.exists(antlr_full_contents):
        G.LOGGER.error('ERROR       : Antlr full contents log not found')
        G.LOGGER.error('Tried to find {0}'.format(antlr_full_contents))
        return E.FILE_NOT_FOUND, G.ANTLR_LOG_FILENAME

    with open(antlr_full_contents, 'r', encoding='utf-8') as antlr_full_file:
        with open(G.ANTLR_LOG_FILENAME, 'w', encoding='utf-8') as antlr_log_file:

            for line in antlr_full_file:
                if not re.search(r'^\[@[0-9]*,[0-9]*:[0-9]*=.*\]$', line):
                    # For example: [@7,52:57='sqlMsg',<IDENTIFIER>,1:52]
                    antlr_log_file.write(line)

    # If the Rules Engine ever needs to read the tokens file, here
    # is the code that would create it.
    #
    # tokens_log_filename	= filename_to_check + '.antlr_tokens.re.log'
    # with open (antlr_full_contents, 'r') as antlr_full_file:
    # 	with antlr_token_file	= open (tokens_log_filename, 'w') as antlr_token_file:
    # 		for line in antlr_full_file:
    # 			if re.search (r'^\[@[0-9]*,[0-9]*:[0-9]*=.*\]$', line):
    # 				antlr_token_file.write (line)

    # -----------------------------------------------------------------------
    if not os.path.exists(G.ANTLR_LOG_FILENAME):
        G.LOGGER.error('ERROR       : Antlr log file not found')
        G.LOGGER.error(f'Tried to find {G.ANTLR_LOG_FILENAME}')
        return E.FILE_NOT_FOUND, G.ANTLR_LOG_FILENAME

    G.ANTLR_LOG_CONTENTS = get_file_contents(G.ANTLR_LOG_FILENAME)

    # The caller should be confident that if ret == 0,
    # the antlr log contents have been read by the line above.

    # Check for issues
    (ret, log_line) = antlr_parse_stmt_check_for_issues()

    if ret != 0:
        report_antlr_issue_parsing_stmt(filename_to_check, ret, log_line)

    else:
        with open(G.ANTLR_LOG_FILENAME, 'a', encoding='utf-8') as log_file:
            fprint(log_file, 'Antlr syntax check succeeded.')

        if G.VERBOSE:
            G.LOGGER.debug((' ' * 15) + 'Good         : Antlr syntax check succeeded')
            G.LOGGER.debug((' ' * 15) + 'Antlr Logfile: {0}'.format(
                G.ANTLR_LOG_FILENAME.replace(G.TEMP_DIR, '$TEMP_DIR')))
            sys.stdout.flush()  # Always flush the console log-file

    return ret
