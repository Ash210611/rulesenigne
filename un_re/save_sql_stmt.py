import un_re.class_definitions as C
import un_re.global_shared_variables as G

from un_re.print_one_sql_statement import print_one_sql_statement
from un_re.write_local_script_name import write_local_script_name


# ======== ========= ========= ========= ========= ========= ========= ==========
def save_sql_stmt(sql_stmt_txt, tentative_command_type):
    sql_stmt_obj = C.SQLStatementObj(
        sql_stmt_num=G.INPUT_FILE.num_statements,
        sql_stmt_txt=sql_stmt_txt,
        command_type='UNKNOWN',
        input_filename=G.INPUT_FILE.input_filename,
        input_filename_rel=G.INPUT_FILE.input_filename_rel,
        antlr_log_filename=G.ANTLR_LOG_FILENAME,
        file_obj=G.INPUT_FILE)

    sql_stmt_obj.tentative_command_type = tentative_command_type

    sql_stmt_obj.local_script_name = write_local_script_name(sql_stmt_txt, G.INPUT_FILE.num_statements)

    G.SQL_STATEMENT_OBJS.append(sql_stmt_obj)

    print_one_sql_statement(sql_stmt_obj)

    G.INPUT_FILE.num_statements += 1
