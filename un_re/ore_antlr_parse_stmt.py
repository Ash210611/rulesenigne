# pylint: disable=C0209           	# Don't require formtted strings

import os  # for path.exists
import re  # for search
import subprocess  # for call
import sys  # for exit

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G

from un_re.antlr_show_context import antlr_show_context
from un_re.fprint import fprint
from un_re.get_file_contents import get_file_contents
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
# This module, ore_antlr_parse_stmt.py, has two improvements over the 
# standard antlr_parse_stmt module:
# - It will directly call the Antlr Grammar Rule based on the tentative command
# - It will timeout after a reasonable number of seconds.
#
# ===============================================================================
def antlr_parse_stmt_check_for_issues(sql_statement):
    issue_dict = {16: 'no viable alternative',
                  # for example: line 120:39 no viable alternative at input '(alignment_cd=...
                  17: 'extraneous input ',
                  # for example, line 20:28 extraneous input ',' expecting {'SYS_CALENDAR.CALENDAR', INTEGER_VALUE,...
                  18: 'mismatched input ',
                  # for example, line 13:14 mismatched input ')' expecting {CASE_N, COLUMN, RANGE_N}
                  19: r'line\b.*?:.*missing.*?at',
                  # for example: line 2:6 missing {T_GO, ';'} at 'IF'
                  20: 'token recognition error'
                  # for example: line 1:26 token recognition error at: '~'
                  }

    for log_line in sql_statement.antlr_log_contents.split('\n'):

        for error_num, search_string in issue_dict.items():

            if re.search(search_string, log_line):
                return error_num, log_line

    return 0, ''


# ===============================================================================
def report_antlr_issue_parsing_stmt(sql_statement, ret, log_line, rule):
    G.RULE_ID = 'g003'

    indent_info(f'Failed to check this statement with Antlr. RET = {ret}')

    antlr_show_context(log_line, sql_statement.temp_sql_filename)

    filename_to_check = sql_statement.temp_sql_filename
    failed_log_filename = filename_to_check + '.failed.antlr.re.log'
    os.rename(sql_statement.antlr_log_filename, failed_log_filename)

    report_firm_finding(
        object_type_nm='FILE',
        object_nm=sql_statement.input_file.input_filename_rel,
        severity=G.RULES[G.RULE_ID].severity,
        message=f'Failed to parse SQL statement using {rule} rule.',
        class_object=sql_statement)

    G.INPUT_FILE.has_a_syntax_error = True


# ===============================================================================
def antlr_parse_stmt_call(os_command):
    try:
        ret = subprocess.call(os_command, shell=True, timeout=G.ANTLR_TIMEOUT_SECONDS)

        if ret < 0:
            G.LOGGER.error('Child was terminated by signal {0}'.format(-ret))
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

    except OSError as e:
        G.LOGGER.error('Antlr execution failed: {0}'.format(e))
        sys.exit(E.ANTLR_EXECUTION_FAILED)

    except subprocess.TimeoutExpired:
        G.LOGGER.warning('Antlr reached time-out limit of {0} seconds.'.format(
            G.ANTLR_TIMEOUT_SECONDS))
        return E.TIMEOUT

    # except FT.TimeoutException:
    # 	G.LOGGER.warning ('Antlr reached time-out limit of {0} seconds.'.format (
    #		G.ANTLR_TIMEOUT_SECONDS))
    #	return E.TIMEOUT

    return 0


# ===============================================================================
Rules = {}
Rules["ALTER TABLE CONSTRAINT"] = 'alter_table'
Rules["ALTER TABLE OTHER"] = 'alter_table'
Rules["ALTER TABLE COLUMN"] = 'alter_table'
Rules["ALTER TABLE PROPERTIES"] = 'alter_table'
Rules["ALTER INDEX"] = 'alter_index'
Rules["ALTER SESSION"] = 'alter_session'
Rules["ALTER USER"] = 'alter_user'
# Rules["ALTER VIEW"  		// Is this used?
Rules["ALTER TRIGGER"] = 'alter_trigger'
Rules["CALL"] = 'procedure_call'
Rules["COMMENT ON COLUMN"] = 'comment_statement'
Rules["COMMENT ON TABLE"] = 'comment_statement'
Rules["COMMENT ON MATERIALIZED VIEW"] = 'comment_statement'
Rules["COMMIT"] = 'commit_statement'
Rules["CREATE DIRECTORY"] = 'create_directory'
Rules["CREATE MATERIALIZED VIEW"] = 'create_materialized_view'
Rules["CREATE PACKAGE BODY"] = 'create_package_body'
Rules["CREATE PACKAGE"] = 'create_package'
Rules["CREATE PROCEDURE"] = 'create_procedure'
Rules["CREATE TRIGGER"] = 'create_trigger'
Rules["CREATE TYPE BODY"] = 'create_type_body'
Rules["CREATE TYPE"] = 'create_type'
Rules["CREATE FUNCTION"] = 'create_function'
Rules["CREATE INDEX"] = 'create_index_statement'
Rules["CREATE SEQUENCE"] = 'create_sequence'
Rules["CREATE TABLE AS SELECT"] = 'create_table'
Rules["CREATE TABLE"] = 'create_table'
Rules["CREATE VIEW"] = 'create_view'
Rules["CREATE USER"] = 'create_user'
Rules["CREATE TABLESPACE"] = 'create_tablespace'
Rules["CREATE ROLE"] = 'create_role'
Rules["CREATE SYNONYM"] = 'create_synonym'
# Rules["DEFAULT DATABASE"		// Is this used?
Rules["DELETE"] = 'delete_statement'
# Rules[No Drop Function?
Rules["DROP DATABASE"] = 'drop_database'
Rules["DROP DISKGROUP"] = 'drop_diskgroup'
Rules["DROP FLASHBACK ARCHIVE"] = 'drop_flashback_archive'
Rules["DROP INDEX"] = 'drop_index'
Rules["DROP MATERIALIZED VIEW"] = 'drop_materialized_view'
Rules["DROP PMEM FILESTORE"] = 'drop_pmem_filestore'
Rules["DROP ROLLBACK SEGMENT"] = 'drop_rollback_segment'
# Rules["DROP PROCEDURE"		// Is this used?
# Rules["DROP SYNONYM"		// Is this used?
# Rules[  No Drop Package?
Rules["DROP PACKAGE BODY"] = 'drop_package_body'
Rules["DROP SEQUENCE"] = 'drop_sequence'
Rules["DROP TABLE"] = 'drop_table'
Rules["DROP TABLESPACE"] = 'drop_tablespace'
Rules["DROP TABLESPACE SET"] = 'drop_tablespace_set'
Rules["DROP TRIGGER"] = 'drop_trigger'
Rules["DROP TYPE"] = 'drop_type'
Rules["DROP USER"] = 'drop_user'
Rules["DROP VIEW"] = 'drop_view'
Rules["EXEC"] = 'exec_command'
Rules["FLASHBACK DATABASE"] = 'flashback_database'
Rules["FLASHBACK TABLE"] = 'flashback_table'
Rules["GRANT"] = 'grant_statement'
Rules["INSERT"] = 'insert_statement'
# Rules[ No Lock table statement?
Rules["MERGE"] = 'merge_statement'
Rules["NOAUDIT"] = 'noaudit'
Rules["PLSQL BLOCK"] = 'plsql_block'
Rules["PURGE"] = 'purge'
Rules["RENAME TABLE"] = 'rename_table'
Rules["REVOKE"] = 'revoke_statement'
# Rules[// No Rollback statements?
Rules["SELECT"] = 'query'
Rules["UPDATE"] = 'update_statement'
Rules["SQLPLUS"] = 'sqlplus_command'
Rules["TRUNCATE TABLE"] = 'truncate_table'
Rules['UNNECESSARY SLASH'] = 'extraneous_slash'
Rules['UNKNOWN'] = 'root'


# ===============================================================================
def get_antlr_rule(sql_statement):
    antlr_rule = 'root'

    if sql_statement.tentative_command_type is not None:
        try:
            antlr_rule = Rules[sql_statement.tentative_command_type]
            return antlr_rule
        except KeyError:
            G.LOGGER.info('No Antlr rule found for {0}'.format(
                sql_statement.tentative_command_type))

    return antlr_rule


# ===============================================================================
def ore_antlr_parse_stmt(grammar, sql_statement):
    '''
    The Antlr function checks syntax of SQL and DDL commands in the
    the LOCAL_SCRIPT_NAME, which is the local copy of the original source
    file for a single statement.

    The antlr_log_content will only contain the output from Antlr actions.
    The antlr_full_log_contents will contain the complete output from Antlr.
    The tokens_log_filename will only contain the tokens from the lexer.

    The antlr_full_contents = tokens_log_filename + G.ANTLR_LOG_FILENAME
    '''

    filename_to_check = sql_statement.temp_sql_filename
    sql_statement.antlr_log_filename = filename_to_check + '.antlr.re.log'
    antlr_full_contents_filename = filename_to_check + '.antlr_full.re.log'

    # Use -XshowSettings to see Java settings
    # grun			= 'java -Xmx3072m -XshowSettings:all org.antlr.v4.gui.TestRig'

    grun = 'java org.antlr.v4.gui.TestRig'

    rule = get_antlr_rule(sql_statement)

    os_command = '{0} {1} {2} -tokens < {3} > {4} 2>&1'.format(
        grun,
        grammar,
        rule,
        sql_statement.temp_sql_filename,
        antlr_full_contents_filename)

    sys.stdout.flush()  # Always flush the console log
    # output before calling a system function.

    sql_statement.antlr_log_contents = ''

    # -----------------------------------------------------------------------
    ret = antlr_parse_stmt_call(os_command)
    sys.stdout.flush()  # Always flush the console log

    if ret == E.TIMEOUT:
        return E.TIMEOUT

    # -----------------------------------------------------------------------
    # If here, ret >= 0
    # Split the full contents into separate files for the tokens and the
    # action outputs.   The tokens can sometimes useful for diagnostics,
    # but it is inefficient for the rules engine to skip past them repeatedly.

    if not os.path.exists(antlr_full_contents_filename):
        G.LOGGER.info('ERROR       : Antlr full contents log not found')
        G.LOGGER.info('Tried to find {0}'.format(antlr_full_contents_filename))
        return E.FILE_NOT_FOUND

    with open(antlr_full_contents_filename, 'r', encoding='utf-8') as antlr_full_file:
        with open(sql_statement.antlr_log_filename, 'w', encoding='utf-8') as antlr_log_file:

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
    if not os.path.exists(sql_statement.antlr_log_filename):
        G.LOGGER.info('ERROR       : Antlr log file not found')
        G.LOGGER.info(f'Tried to find {sql_statement.antlr_log_filename}')
        return E.FILE_NOT_FOUND

    sql_statement.antlr_log_contents = get_file_contents(sql_statement.antlr_log_filename)

    # The caller should be confident that if ret == 0,
    # the antlr log contents have been read by the line above.

    # Check for issues
    (ret, log_line) = antlr_parse_stmt_check_for_issues(sql_statement)

    if ret != 0:
        report_antlr_issue_parsing_stmt(sql_statement, ret, log_line, rule)

    else:
        with open(sql_statement.antlr_log_filename, 'a', encoding='utf-8') as log_file:
            fprint(log_file, 'Antlr syntax check succeeded.')

        G.LOGGER.debug((' ' * 15) + 'Good         : Antlr syntax check succeeded')
        G.LOGGER.debug((' ' * 15) + 'Antlr Logfile: {0}'.format(
            sql_statement.antlr_log_filename.replace(G.TEMP_DIR, '$TEMP_DIR')))
        sys.stdout.flush()  # Always flush the console log-file

    return ret
