# pylint: disable=C0209			# Don't require formatted strings.

import os
import sys

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G

from un_re.antlr_parse_stmt import antlr_parse_stmt
from un_re.classify_command_type import classify_file_contents_with_regex
from un_re.indent_info import indent_info
from un_re.indent_warning import indent_warning
from un_re.print_msg import print_msg
from un_re.classify_command_type import classify_input_statement_command_type


# ===============================================================================
# noinspection PyUnusedLocal
def process_one_sql_stmt(sql_stmt_obj):
    '''
    This function is called by the process_one_sql_file() function once for
    each SQL statement in that file.
    '''
    ret = 0
    G.LOGGER.info('Parsing      : {0}'.format(
        sql_stmt_obj.local_script_name.replace(G.TEMP_DIR + '/', '')))

    G.SQL_STMT_NUM = sql_stmt_obj.sql_stmt_num
    sql_stmt_obj.sql_stmt_txt = sql_stmt_obj.sql_stmt_txt.rstrip()
    G.LOCAL_SCRIPT_NAME = sql_stmt_obj.local_script_name

    sql_stmt_obj.tentative_command_type = classify_file_contents_with_regex(sql_stmt_obj.sql_stmt_txt)
    indent_info('Tentative cmd: {0}'.format(sql_stmt_obj.tentative_command_type))

    if G.RULES_ENGINE_TYPE in (
            'TERADATA_DDL', 'TERADATA_DML', 'DAMODRE'):

        if sql_stmt_obj.tentative_command_type in (
                'COMMENT ON TABLE'
                'COMMENT ON COLUMN'):

            ret = antlr_parse_stmt('TD15_comment_on', G.LOCAL_SCRIPT_NAME)

        else:
            ret = antlr_parse_stmt('TD16', G.LOCAL_SCRIPT_NAME)

    elif G.RULES_ENGINE_TYPE == 'HIVE_DDL_RE':
        ret = antlr_parse_stmt('Hplsql', G.LOCAL_SCRIPT_NAME)

    elif G.RULES_ENGINE_TYPE == 'PG_RE':
        ret = antlr_parse_stmt('PG', G.LOCAL_SCRIPT_NAME)

    elif G.RULES_ENGINE_TYPE == 'REDSHIFT':
        ret = antlr_parse_stmt('REDSHIFT', G.LOCAL_SCRIPT_NAME)

    else:
        print_msg('{0}: Unknown RULES_ENGINE_TYPE: {1}'.format(
            os.path.basename(__file__),
            G.RULES_ENGINE_TYPE))
        sys.exit(E.UNKNOWN_RULES_ENGINE_TYPE)

    sql_stmt_obj.antlr_log_filename = G.ANTLR_LOG_FILENAME
    sql_stmt_obj.antlr_log_contents = G.ANTLR_LOG_CONTENTS
    if ret == 0:
        sql_stmt_obj.antlr_status = 'SUCCEEDED'
        classify_input_statement_command_type(sql_stmt_obj)
        indent_info('Command type : {0}'.format(sql_stmt_obj.command_type))
        if sql_stmt_obj.tentative_command_type != sql_stmt_obj.command_type:
            indent_warning('WARNING-g005 : Tentative command type does not match parsed.')

    else:
        sql_stmt_obj.antlr_status = 'FAILED'

    # This function can run in parallel.
    # In other words, all the Antlr parsing can run in parallel.
    # Antlr parsing is time consuming, so that maximizes parallel throughput.
    # After Antlr parses all the input files, the calling function will read
    # the Antlr findings from the Antlr log file.

    return ret
