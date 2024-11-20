# pylint: 	disable=C0209			# Don't require formatted strings.

import os  # For os.path.isfile
import re  # For re.search
import sys  # for sys.exit

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G
from un_re.clean_file import clean_file
from un_re.clean_one_dreml_statement import clean_one_dreml_statement
from un_re.clean_one_hive_statement import clean_one_hive_statement
from un_re.dreml_extract_sql_stmts import dreml_extract_sql_stmts
from un_re.extract_sql_stmts_from_sql_file import extract_sql_stmts_from_sql_file
from un_re.indent_info import indent_info
from un_re.is_a_dml_statement import is_a_dml_statement
from un_re.prepare_stmt import prepare_stmt
from un_re.print_msg import print_msg
from un_re.save_sql_stmt import save_sql_stmt


# ===============================================================================
def clean_and_prepare(these_sql_statements):
    num_sql_statements = 0
    for sql_stmt_txt in these_sql_statements:

        if G.RULES_ENGINE_TYPE in ('TERADATA_DDL', 'DAMODRE'):
            sql_stmt_txt = prepare_stmt(sql_stmt_txt)

        elif G.RULES_ENGINE_TYPE == 'TERADATA_DML':
            sql_stmt_txt = clean_one_dreml_statement(sql_stmt_txt)
        # print ('After clean_one_dreml_statement: {0}'.format (G.SQL_STATEMENT))

        elif G.RULES_ENGINE_TYPE == 'HIVE_DDL_RE':
            sql_stmt_txt = clean_one_hive_statement(sql_stmt_txt)

            one_line_sql = sql_stmt_txt.replace('\n', '')
            # print (one_line_sql)
            if re.search('>>', one_line_sql):
                G.RULE_ID = 'g003'

                print_msg('{0}-g003 : Cannot parse JSON DDL format in {1}'.format(
                    G.RULES[G.RULE_ID].severity,
                    os.path.basename(G.INPUT_FILENAME)))
                for file_obj in G.INPUT_FILES:
                    if file_obj.input_filename_rel == G.INPUT_FILENAME_REL:
                        # Mark it now to be reported later by the
                        # check_g003 function.
                        file_obj.has_a_syntax_error = True
                        break

                continue
            # DO NOT add this statement to the list
            # of all sql statements, and do not
            # check rules for that statement

        # Write-out the sql_statement after cleaning
        save_sql_stmt(sql_stmt_txt, tentative_command_type='UNKNOWN')

        num_sql_statements += 1

    return num_sql_statements


# ===============================================================================
def get_all_sql_statements():
    G.LOGGER.info('Getting all SQL statements...')

    num_stmts_to_process = 0
    for G.FILE_NUM in range(len(G.FILE_DICT)):

        G.INPUT_FILE = G.INPUT_FILES[G.FILE_NUM]
        G.INPUT_FILENAME_REL = G.FILE_DICT[G.FILE_NUM]

        if G.RULES_ENGINE_TYPE == 'TERADATA_DDL':
            G.INPUT_FILENAME = G.XML_DIR + '/' + G.FILE_DICT[G.FILE_NUM]
        else:
            G.INPUT_FILENAME = G.INPUT_DIR + '/' + G.FILE_DICT[G.FILE_NUM]

        if not os.path.isfile(G.INPUT_FILENAME):
            print_msg("ERROR.         This filename is not found.")
            G.LOGGER.error('Tried to find: {0}'.format(G.INPUT_FILENAME))
            G.LOGGER.error('Input_filename_rel: {0}'.format(G.INPUT_FILENAME_REL))
            G.LOGGER.error('')
            sys.exit(E.FILE_NOT_FOUND)

        # ---------------------------------------------------------------
        G.LOGGER.info('')
        indent_info('=' * 72)
        indent_info('Filename: {0}'.format(G.INPUT_FILENAME_REL))

        if not G.INPUT_FILE.is_utf8_readable:
            continue  # Is not utf-8 readable

        # ---------------------------------------------------------------
        if G.RULES_ENGINE_TYPE in (
                'TERADATA_DDL', 'TERADATA_DML', 'DAMODRE',
                'HIVE_DDL_RE'):

            clean_file(G.INPUT_FILE.input_filename)

        elif G.RULES_ENGINE_TYPE in ('DATA_MODEL',
                                     'PG_RE',
                                     'DB2_RE',
                                     'SNOWFLAKE',
                                     'DATABRICKS',
                                     'REDSHIFT'):

            pass

        else:
            G.LOGGER.error('Error: Unknown Rules Engine Type in {0}'.format(__file__))
            print_msg('{0}: Unknown RULES_ENGINE_TYPE: {1}'.format(
                os.path.basename(__file__),
                G.RULES_ENGINE_TYPE))
            sys.exit(E.UNKNOWN_RULES_ENGINE_TYPE)

        indent_info('The following statements were found:')

        # ---------------------------------------------------------------
        # Extract the SQL statements from each input file.

        if G.RULES_ENGINE_TYPE == 'TERADATA_DML':

            # DREML reads SQL from several additional types of input files
            these_sql_statements = dreml_extract_sql_stmts(G.FILE_NUM, G.INPUT_FILENAME)

            # Remove the statements that are not actually DML statements.
            # List comprehension method
            these_sql_statements[:] = [sql for sql in these_sql_statements if is_a_dml_statement(sql)]

        # Alternative method
        # https://stackoverflow.com/questions/1207406/how-to-remove-items-from-a-list-while-iterating
        # temp = []
        # while somelist:
        #     x = somelist.pop()
        #     if not determine(x):
        #         temp.append(x)
        # while temp:
        #     somelist.append(templist.pop())

        else:
            these_sql_statements = extract_sql_stmts_from_sql_file(G.INPUT_FILENAME)

        # We must clean and prepare the statements before parsing them in
        # parallel, because the parallel workers can't send the cleaned SQL back.
        num_stmts_to_process += clean_and_prepare(these_sql_statements)

    G.LOGGER.info('Num Files to Process = {0}'.format(len(G.FILE_DICT)))
    G.LOGGER.info('Num Stmts to Process = {0}'.format(num_stmts_to_process))
