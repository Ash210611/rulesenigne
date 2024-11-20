# pylint: disable=C0209           # Don't require formtted strings
# pylint: disable=R0912           # Allow more branches

import os
import re
import sys

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G

from un_re.ore_antlr_parse_stmt import ore_antlr_parse_stmt
from un_re.classify_command_type import classify_input_statement_command_type
from un_re.classify_command_type import classify_statement_with_regex
from un_re.count_command_type import count_command_type
from un_re.fprint import fprint
from un_re.indent_info import indent_info
from un_re.indent_warning import indent_warning
from un_re.print_command_summary import print_command_summary
from un_re.print_msg import print_msg
from un_re.ore_transfer_parsed_attributes import ore_transfer_parsed_attributes


# ======== ========= ========= ========= ========= ========= ========= ==========
def save_temp_sql_filename(sql_statement_obj):
    '''
    Consider moving this into the class definition for the sql_statement
    '''

    if re.search('clean', sql_statement_obj.input_file.input_filename_rel):
        stmt_num = sql_statement_obj.sql_stmt_num
    # And actually, it will equal 0 at the point.
    # The 'clean' file, is the whole input file after cleaning.
    else:
        stmt_num = sql_statement_obj.sql_stmt_num + 1

    sql_statement_obj.temp_sql_filename = '{0}/{1}.{2}.sql'.format(
        G.TEMP_DIR,
        sql_statement_obj.input_file.input_filename_rel,
        stmt_num)

    temp_dir = os.path.split(sql_statement_obj.temp_sql_filename)[0]
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    with open(sql_statement_obj.temp_sql_filename, 'w', encoding='utf-8') as temp_sql_file:
        fprint(temp_sql_file, sql_statement_obj.sql_stmt_txt)

    if not os.path.exists(sql_statement_obj.temp_sql_filename):
        G.LOGGER.error('Failed to create temp_sql_filename')
        sys.exit(E.FILE_NOT_FOUND)


# ======== ========= ========= ========= ========= ========= ========= ==========
def should_skip_parsing_this_statement(stmt_obj):
    # Return False while testing the get_antlr_rule function.
    # Don't skip anything yet.

    if stmt_obj.tentative_command_type in (
            'ALTER TRIGGER',
            'COMMIT',
            'CREATE FUNCTION',
            'CREATE PACKAGE',
            'CREATE PACKAGE BODY',
            'CREATE PROCEDURE',
            'CREATE SYNONYM',
            'CREATE TRIGGER',
            'CREATE TYPE',
            'DELETE',
            'INSERT',
            'MERGE',
            'PLSQL BLOCK',
            'SELECT',
            'SQLPLUS',
            'UNNECESSARY SLASH',
            'UPDATE'):
        return True

    return False


# ======== ========= ========= ========= ========= ========= ========= ==========
def parse_1_sql_statement():
    '''
    Make a quick regex scan to guess what kind of statement this is.

    If we have no idea what kind of statement this is, do NOT waste time
    scanning it with Antlr.

    This Oracle rules engine will have UNKNOWN statements when PL/SQL is
    used to generate EXECUTE IMMEDIATE commands from variables.
    '''

    save_temp_sql_filename(G.SQL_STATEMENT_OBJ)

    filename_to_check = G.SQL_STATEMENT_OBJ.temp_sql_filename
    G.LOGGER.info('Parsing {0}'.format(
        filename_to_check.replace(G.TEMP_DIR, '$TEMP_DIR')))

    G.SQL_STATEMENT_OBJ.tentative_command_type = classify_statement_with_regex(G.SQL_STATEMENT_OBJ.sql_stmt_txt)

    indent_info('Tentative cmd: {0}'.format(G.SQL_STATEMENT_OBJ.tentative_command_type))
    if G.SQL_STATEMENT_OBJ.tentative_command_type == 'UNKNOWN':
        if len(G.SQL_STATEMENT_OBJ.sql_stmt_txt) > 20:
            snippet = G.SQL_STATEMENT_OBJ.sql_stmt_txt[0:20]
        else:
            snippet = G.SQL_STATEMENT_OBJ.sql_stmt_txt
        if re.search(r'\s', G.SQL_STATEMENT_OBJ.sql_stmt_txt, re.IGNORECASE | re.DOTALL):
            indent_info(f'WARNING-g005 : Unknown command: {snippet}')
        else:
            indent_info(f'Dynamic SQL? : {snippet}')

    if G.SQL_STATEMENT_OBJ.tentative_command_type == 'UNKNOWN':
        G.SQL_STATEMENT_OBJ.command_type = G.SQL_STATEMENT_OBJ.tentative_command_type
        indent_info('COMMAND TYPE = UNKNOWN')
        ret = -1

    elif should_skip_parsing_this_statement(G.SQL_STATEMENT_OBJ):

        G.SQL_STATEMENT_OBJ.command_type = G.SQL_STATEMENT_OBJ.tentative_command_type
        indent_info('               We will skip parsing this command.')
        ret = 0

    else:
        # Only parse the statement if we can recognize it to start with.
        ret = ore_antlr_parse_stmt('ORA23', G.SQL_STATEMENT_OBJ)

        if ret == 0:

            G.SQL_STATEMENT_OBJ.antlr_status = 'SUCCEEDED'

            G.SQL_STATEMENT_OBJ.command_type = classify_input_statement_command_type(
                G.SQL_STATEMENT_OBJ)

            indent_info(f'COMMAND TYPE = {G.SQL_STATEMENT_OBJ.command_type}')
            # if G.SQL_STATEMENT_OBJ.tentative_command_type != G.SQL_STATEMENT_OBJ.command_type and \
            # 	G.SQL_STATEMENT_OBJ.command_type != 'CALL':
            if G.SQL_STATEMENT_OBJ.command_type not in (G.SQL_STATEMENT_OBJ.tentative_command_type, 'CALL'):
                indent_info('Notice       : Tentative command type changed.')
            # Calls cannot be compared in Oracle because they might not
            # contain a parameter list.   An Oracle call might be
            # as simple as "v_sql;", which could be anything

            ore_transfer_parsed_attributes(G.SQL_STATEMENT_OBJ)

        else:
            G.SQL_STATEMENT_OBJ.command_type = G.SQL_STATEMENT_OBJ.tentative_command_type

    count_command_type(G.SQL_STATEMENT_OBJ.command_type)

    if G.SQL_STATEMENT_OBJ.command_type in G.SQL_STATEMENT_OBJ.input_file.command_counter:
        G.SQL_STATEMENT_OBJ.input_file.command_counter[G.SQL_STATEMENT_OBJ.command_type] += 1
    else:
        G.SQL_STATEMENT_OBJ.input_file.command_counter[G.SQL_STATEMENT_OBJ.command_type] = 1

    return ret


# It would be recommended to skip checking any other
# SQL statements in that same file.

# ======== ========= ========= ========= ========= ========= ========= ==========
def loop_through_statements():
    prev_filenum = -1
    skip_remaining_stmts_in_this_file = False

    for G.SQL_STATEMENT_OBJ in G.SQL_STATEMENT_OBJS:

        if G.SQL_STATEMENT_OBJ.input_file.filenum != prev_filenum:
            skip_remaining_stmts_in_this_file = False

        if skip_remaining_stmts_in_this_file:
            G.SQL_STATEMENT_OBJ.antlr_status = 'SKIPPED'

        else:
            ret = parse_1_sql_statement()

            if ret != 0:
                G.SQL_STATEMENT_OBJ.antlr_status = 'FAILED'
                skip_remaining_stmts_in_this_file = True

            else:
                for k, v in G.SQL_STATEMENT_OBJ.input_file.command_counter.items():
                    if v >= G.MAX_CMDS_PER_TYPE_PER_FILE:
                        print_msg('WARNING      : Reached limit of {0} {1} stmts in {2}'.format(
                            G.MAX_CMDS_PER_TYPE_PER_FILE,
                            k,
                            G.SQL_STATEMENT_OBJ.input_filename_rel))
                        indent_warning('Recommended to move statements to multiple files, or to ETL.')
                        skip_remaining_stmts_in_this_file = True

        prev_filenum = G.SQL_STATEMENT_OBJ.input_file.filenum


# ======== ========= ========= ========= ========= ========= ========= ==========
def ore_parse_sql_statements():
    '''
    This rules engine runs in Python.
    Antlr runs in Java, so the sql statements cannot be passed in memory.
    Each sql statment is saved to a temp file before parsing it.

    After parsing each statement, figure out what kind of command it was,
    and transfer the attributes observed during parsing to the class
    instance.
    '''

    G.LOGGER.info('=' * 88)
    G.LOGGER.info('Parsing SQL statements...')

    if len(G.SQL_STATEMENT_OBJS) == 0:
        G.LOGGER.info('')
        indent_info('Actually, no SQL statements were found to parse.')
        return

    loop_through_statements()

    if G.PARALLEL_DEGREE == 1:
        print_command_summary()
