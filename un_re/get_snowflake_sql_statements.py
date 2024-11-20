# pylint: 	disable=C0209			# Don't require formatted strings.

import re  # For re.search

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.antlr_parse_stmt import antlr_parse_stmt
from un_re.classify_command_type import classify_file_contents_with_regex
from un_re.count_command_type import count_command_type
from un_re.get_antlr_findings import add_column_element
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.print_command_summary import print_command_summary
from un_re.print_one_sql_statement import print_one_sql_statement
from un_re.rezero_the_command_counters import rezero_the_command_counters
from un_re.split_name_parts import split_name_parts
from un_re.split_value_from_line import split_value_from_line
from un_re.write_local_script_name import write_local_script_name


# ===============================================================================
# This module is very similar to the nearby module for DB2, and the one for
# DATABRICKS.
#
# For other RULES_ENGINE_TYPEs, we split the SQL statements on a semi-colon
#
# For SNOWFLAKE, like DB2, and soon to be like Oracle, we will let Antlr 
# split the SQL statements, which may or may not terminate with a semi-colon
#
# That is why the functions in this module are different and separate from the 
# functions in the get_antlr_findings module.
#
# It is tempting to think we could have 1 module that could work for all
# rules engine types, but each language has small differences, for example
# the way they declare comments on tables and columns
#
# ===============================================================================
def create_snowflake_sql_statement_obj(AA):
    AA.sql_stmt_txt = AA.sql_stmt_txt.rstrip()
    G.SQL_STATEMENT_OBJ = C.SQLStatementObj(G.SQL_STMT_NUM,
                                            AA.sql_stmt_txt,
                                            command_type=AA.statement_type,
                                            input_filename=AA.file_obj.input_filename,
                                            input_filename_rel=AA.file_obj.input_filename_rel,
                                            antlr_log_filename=G.ANTLR_LOG_FILENAME,
                                            file_obj=AA.file_obj)

    G.SQL_STATEMENT_OBJ.tentative_command_type = AA.tentative_command_type

    G.SQL_STATEMENT_OBJS.append(G.SQL_STATEMENT_OBJ)


# ===============================================================================
def create_table_object(AA):
    if AA.database_base == 'UNKNOWN':
        if G.DATABASE_BASE_DEFAULT is not None:
            AA.database_base = G.DATABASE_BASE_DEFAULT

    G.TABLE_STRUCTURE = C.TableStructure(
        AA.database_base,
        AA.table_name,
        G.SQL_STATEMENT_OBJ)

    G.TABLE_STRUCTURE.naming_method, G.TABLE_STRUCTURE.table_name_tokens = \
        split_name_parts(
            source='TABLE',
            input_name=G.TABLE_STRUCTURE.table_name_orig,
            table_naming_method='UNKNOWN')

    for column_descriptor in AA.column_descriptors:
        column_name, datatype = column_descriptor.split('|')

        add_column_element(column_name, datatype,
                           title='',
                           is_identity=False)

    G.TABLE_STRUCTURE.sql_stmt_obj = G.SQL_STATEMENT_OBJ
    G.TABLE_STRUCTURE.primary_key_is_specified = AA.primary_key_is_specified

    G.TABLE_STRUCTURES.append(G.TABLE_STRUCTURE)


# ===============================================================================
def display_snowflake_statement(AA):
    print_one_sql_statement(G.SQL_STATEMENT_OBJ)
    G.LOGGER.info('')
    indent(f'Tentative cmd: {AA.tentative_command_type}')
    indent(f'Command Type : {AA.statement_type}')

    if AA.statement_type in ('ALTER TABLE', 'CREATE TABLE'):
        indent(f'Schema Name  : {AA.database_base}')
        indent(f'Table Name   : {AA.table_name}')
    elif AA.statement_type == 'SET SCHEMA':
        indent(f'Schema Name  : {G.DATABASE_BASE_DEFAULT}')


# ===============================================================================
def get_snowflake_sql_statements_from_antlr_log(file_obj):
    # SQL Statements are numbered within each file separately.
    G.SQL_STMT_NUM = 0

    # The following class will collect the various attributes we need to
    # observe from any SQL statement.
    AA = C.AntlrAttributes(file_obj)

    G.DATABASE_BASE_DEFAULT = None

    rezero_the_command_counters()

    with open(G.ANTLR_LOG_FILENAME, 'rt', encoding='utf-8') as antlr_log:
        for line in antlr_log.readlines():

            if re.search(r'^Statement Type               :', line):
                AA.statement_type = split_value_from_line(line)

            elif re.search(r'^Parsed single_statement      :', line):
                AA.read_sql_stmt_txt = True

            elif re.search(r'^End of parsed single stmt    :', line):
                AA.tentative_command_type = classify_file_contents_with_regex(AA.sql_stmt_txt)

                create_snowflake_sql_statement_obj(AA)

                if AA.statement_type in ('ALTER TABLE', 'CREATE TABLE'):
                    create_table_object(AA)

                display_snowflake_statement(AA)

                count_command_type(AA.statement_type)

                # Reinitialize the loop variables
                AA = C.AntlrAttributes(file_obj)

                G.SQL_STMT_NUM += 1

            elif re.search(r'Found database identifier    :', line):
                AA.database_base = split_value_from_line(line)
                G.DATABASE_BASE_DEFAULT = AA.database_base

            elif re.search(r'Found table name             :', line):
                AA.table_name = split_value_from_line(line)

            elif re.search(r'Found primary key            :', line):
                AA.primary_key_is_specified = True

            elif re.search(r'Found default schema         :', line):
                G.DATABASE_BASE_DEFAULT = split_value_from_line(line)

            elif re.search(r'Found column name            :', line):
                column_name = split_value_from_line(line)

            elif re.search(r'  datatype                   :', line):
                datatype = split_value_from_line(line)
                column_descriptor = f'{column_name}|{datatype}'
                AA.column_descriptors.append(column_descriptor)

            elif AA.read_sql_stmt_txt:
                AA.sql_stmt_txt += line

    G.LOGGER.info('')
    print_command_summary()


# ===============================================================================
def get_snowflake_sql_statements_from_one_file(file_obj):
    # ---------------------------------------------------------------
    # Extract the SQL statements from each input file.

    sql_txt = get_file_contents(file_obj.input_filename)

    G.LOCAL_SCRIPT_NAME = write_local_script_name(sql_txt)

    ret = antlr_parse_stmt('SNOWFLAKE', G.LOCAL_SCRIPT_NAME)

    if ret == 0:
        get_snowflake_sql_statements_from_antlr_log(file_obj)


# ===============================================================================
def get_snowflake_sql_statements():
    G.LOGGER.info('Num Files to Process = {0}'.format(len(G.FILE_DICT)))
    G.LOGGER.info('Reading all SNOWFLAKE files...')
    for G.FILE_NUM in range(len(G.FILE_DICT)):

        file_obj = G.INPUT_FILES[G.FILE_NUM]

        if file_obj.is_utf8_readable:
            get_snowflake_sql_statements_from_one_file(file_obj)
