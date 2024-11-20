import os

import un_re.global_shared_variables as G

from un_re.get_file_contents import get_file_contents


# ===============================================================================
def refresh_sql_statement_objs():
    for sql_stmt_obj in G.SQL_STATEMENT_OBJS:

        succeeded_antlr_log_filename = sql_stmt_obj.local_script_name + '.antlr.re.log'
        if os.path.exists(succeeded_antlr_log_filename):
            sql_stmt_obj.antlr_log_filename = succeeded_antlr_log_filename
            sql_stmt_obj.antlr_status = 'SUCCEEDED'
            sql_stmt_obj.antlr_log_contents = get_file_contents(succeeded_antlr_log_filename)
            continue

        failed_antlr_log_filename = sql_stmt_obj.local_script_name + '.failed.antlr.re.log'
        if os.path.exists(failed_antlr_log_filename):
            sql_stmt_obj.antlr_log_filename = failed_antlr_log_filename
            sql_stmt_obj.antlr_status = 'FAILED'
            continue

        skipped_antlr_log_filename = sql_stmt_obj.local_script_name + '.skipped.antlr.re.log'
        if os.path.exists(skipped_antlr_log_filename):
            sql_stmt_obj.antlr_log_filename = skipped_antlr_log_filename
            sql_stmt_obj.antlr_status = 'SKIPPED'
