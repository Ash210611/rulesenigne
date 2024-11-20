# pylint: disable=C0209           # Don't require formtted strings

import os
import re
import time

import un_re.class_definitions as C
import un_re.global_shared_variables as G

from un_re.ore_antlr_parse_stmt import ore_antlr_parse_stmt
from un_re.check_r416 import check_r416
from un_re.classify_command_type import classify_statement_with_regex
from un_re.fprint import fprint
from un_re.indent_info import indent_info
from un_re.indent_warning import indent_warning
from un_re.remove_comments import remove_comments_alt
from un_re.remove_sqlplus_prompts import remove_sqlplus_prompts
from un_re.remove_leading_blank_lines import remove_leading_blank_lines
from un_re.ore_parse_sql_statements import save_temp_sql_filename
from un_re.save_sql_stmt import save_sql_stmt
from un_re.split_value_from_line import split_value_from_line


class TimeoutException(Exception):
    pass


# ======== ========= ========= ========= ========= ========= ========= ==========
def clean_stmt(stmt):
    # print (f'Stmt v1={stmt}')

    # If the entire stmt is wrapped in parens, remove the parens
    remove_parens = re.compile(r"^\((.*?)\)$", re.DOTALL)
    stmt = remove_parens.sub(r'\1', stmt)
    # print (f'Stmt after removing parens={stmt}')

    # Example 1:
    # CREATE TABLE ' ||v_own_nm1||'.'||v_tbl_nm1||' AS    SELECT * FROM '||v_own_nm1||'.'||v_tbl_nm2

    # Convert that to
    # CREATE TABLE v_own_nm1.v_tbl_nm1 AS    SELECT * FROM v_own_nm1.v_tbl_nm2
    # regex_1 = re.compile ( r"\'\s?\|\|(.*?)\|\|\'", re.DOTALL )
    regex_1 = re.compile(r"\'\s*\|\|\s*(.*?)\s*\|\|\s*\'", re.DOTALL)
    stmt = regex_1.sub(r'\1', stmt)
    # \1 refers to the first capture group in parenthesis, ".*?"

    # print (f'Stmt v2={stmt}')
    # Convert that to
    # 'CREATE TABLE v_own_nm1.v_tbl_nm1 AS    SELECT * FROM v_own_nm1.v_tbl_nm2
    regex_2 = re.compile(r"\'\s?\|\|(.*?)", re.DOTALL)
    stmt = regex_2.sub(r'\1', stmt)

    # print (f'Stmt v3={stmt}')
    # Remove the leading and trailing single quotes
    regex_3 = re.compile(r"^\'(.*?)\'$", re.DOTALL)
    stmt = regex_3.sub(r'\1', stmt)

    # print (f'Stmt v4={stmt}')
    # Replace embedded double-single quotes
    stmt = stmt.replace("''", "'")

    # print (f'Stmt v5={stmt}')
    stmt = stmt.lstrip("'")

    # print (f'Stmt Final={stmt}')
    return stmt


# ======== ========= ========= ========= ========= ========= ========= ==========
def clean_shell_variables(stmt):
    # Remove dollar-curly's, which start some temporary variables
    # Change ${sqlplus.whenever.sqlerror}
    # To     A_Shell_Variable
    regex4 = re.compile(r'\${sqlplus.whenever.sqlerror}')
    new_stmt = regex4.sub(r'EXIT Some_Value', stmt)
    if new_stmt != stmt:
        stmt = new_stmt

    # Remove curly bracket variables
    regex_curly = re.compile(r'\${.*?}')
    stmt = regex_curly.sub('SHELL_VARIABLE', stmt)

    return stmt


# ======== ========= ========= ========= ========= ========= ========= ==========
def extract_sql_stmts_from_antlr(temp_sql_obj):
    stmt = ''
    found_stmt = False
    command_type = ''
    found_ei_stmt = False

    for line in temp_sql_obj.antlr_log_contents.split('\n'):
        if re.search('Statement Type               :', line):
            command_type = split_value_from_line(line)

        if found_ei_stmt:
            # extract the EXECUTE IMMEDIATE statements
            if re.search('  Execute Immediate Done', line):
                # stmt = stmt.rstrip ("'")
                stmt = clean_stmt(stmt)
                stmt = stmt + ';'
                tentative_command_type = classify_statement_with_regex(stmt)
                save_sql_stmt(stmt, tentative_command_type)
                found_ei_stmt = False
            # We are done with that statement now.
            elif found_ei_stmt:
                if re.search('  Execute Immediate Expr     : ', line):
                    stmt = split_value_from_line(line)
                # stmt = stmt.strip ("'")

                else:
                    stmt += ('\n' + line)
        elif re.search('Sub-statement Type           : EXECUTE IMMEDIATE', line):
            found_ei_stmt = True
            # We will read the text on the next line
            stmt = ''

        else:
            if re.search('Parsed single_statement      :', line):
                found_stmt = True
                stmt = ''
            elif re.search('End of parsed single stmt    : ', line):
                found_stmt = False
                stmt = stmt.strip()
                save_sql_stmt(stmt, command_type)
            elif found_stmt:
                stmt += (line + '\n')


# ======== ========= ========= ========= ========= ========= ========= ==========
def extract_from_one_file(clean_contents):
    '''
    Extracting statements from Oracle DDL files is challenging because of
    PL/SQL.   You cannot simply delimit statements on a semi-colon, because
    a PL/SQL block can contain multiple statements.  And PL/SQL blocks can
    be nested inside other PL/SQL blocks.

    Antlr can parse it because of the way it setups a search tree and uses
    recursion.  And Antlr can parse any number of statements from a single
    input file.

    For those reasons, we will let Antlr parse the whole file first,
    and extract the SQL statements from that.
    '''

    # Setup a temporary file so that Antlr can parse it
    temp_filename_rel = os.path.splitext(G.INPUT_FILE.input_filename_rel)[0] + '.clean.sql'
    temp_filename = os.path.join(G.TEMP_DIR, temp_filename_rel)
    temp_dirname = os.path.dirname(temp_filename)
    if not os.path.exists(temp_dirname):
        os.makedirs(temp_dirname)

    with open(temp_filename, 'w', encoding='utf-8') as temp_file:
        fprint(temp_file, clean_contents)

    temp_input_file = C.InputFile(
        filenum=0,
        input_filename=temp_filename,
        input_filename_rel=temp_filename_rel)

    temp_sql_obj = C.SQLStatementObj(
        sql_stmt_num=0,
        sql_stmt_txt=clean_contents,
        command_type='UNKNOWN',
        input_filename=temp_filename,
        input_filename_rel=temp_filename_rel,
        antlr_log_filename=None,
        file_obj=temp_input_file)

    save_temp_sql_filename(temp_sql_obj)

    temp_input_file.num_statements = 1

    try:
        ret = ore_antlr_parse_stmt('ORA23', temp_sql_obj)

        if ret == 0:
            extract_sql_stmts_from_antlr(temp_sql_obj)

    except TimeoutException:
        indent_warning('Antlr timeout.')


# ======== ========= ========= ========= ========= ========= ========= ==========
def ore_extract_sql_statements():
    for G.INPUT_FILE in G.INPUT_FILES:
        G.LOGGER.info('=' * 88)
        G.LOGGER.info('File Number  = {0}, started at {1}.'.format(
            G.INPUT_FILE.filenum + 1,
            time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime())))

        filename = G.INPUT_FILE.input_filename.replace(G.WORKSPACE, '$WORKSPACE')
        G.LOGGER.info(f'Location     = {filename}, Lines = {G.INPUT_FILE.num_lines}')

        if not G.INPUT_FILE.is_utf8_readable:
            indent_info('Skipped, is not utf8-readable.')
            continue

        # Check rules that apply to the whole filename here
        if 'r416' in G.SHOULD_CHECK_RULE:
            ret = check_r416(G.INPUT_FILE.input_filename)  # no control characters
            if ret != 0:
                continue

        clean_contents = remove_comments_alt(G.INPUT_FILE.contents)
        clean_contents = clean_shell_variables(clean_contents)
        clean_contents = remove_sqlplus_prompts(clean_contents)
        clean_contents = remove_leading_blank_lines(clean_contents)

        extract_from_one_file(clean_contents)
        # Calling that function will set G.INPUT_FILE.num_statements

        G.LOGGER.info('')

        if G.INPUT_FILE.num_statements == 1:
            G.LOGGER.info('File {0} has 1 statement to process.'.format(
                G.INPUT_FILE.filenum + 1))

        else:
            G.LOGGER.info('File {0} has {1} statements to process.'.format(
                G.INPUT_FILE.filenum + 1,
                G.INPUT_FILE.num_statements))

        G.LOGGER.info('File {0}, {1}, is read at {2}.'.format(
            G.INPUT_FILE.filenum + 1,
            G.INPUT_FILE.input_filename.replace(G.WORKSPACE, '$WORKSPACE'),
            time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime())))

    G.LOGGER.info('')
