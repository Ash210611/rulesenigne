# pylint: 	disable=C0209			# Don't require formatted strings.

import re  # For re.search

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.antlr_parse_stmt import antlr_parse_stmt
from un_re.classify_command_type import classify_file_contents_with_regex
from un_re.count_command_type import count_command_type
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.print_command_summary import print_command_summary
from un_re.print_one_sql_statement import print_one_sql_statement
from un_re.rezero_the_command_counters import rezero_the_command_counters
from un_re.split_name_parts import split_name_parts
from un_re.split_value_from_line import split_value_from_line
from un_re.write_local_script_name import write_local_script_name


# ===============================================================================
# For other Rules Engine Types, observations are extracted from the 
# ANTLR_LOG_FILENAME using functions in the get_antlr_findings module.
#
# We can't use those functions for extracting DB2 observations because those
# functions operate on SQL statements that have been split into separtate files
# and that enables them to make multiple passes through the ANTLR_LOG_FILENAME.
#
# For DB2, we are using Antlr to parse all the SQL statements in the file 
# without splitting them apart, so the observations have to be extracted in one
# pass.
#
# That is why the functions in this module are different and separate from the 
# functions in the get_antlr_findings module.
#
# ===============================================================================
def create_sql_statement_obj(AA):
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
def add_db2_column_element(column_name, datatype, comment_txt, is_identity):
    """
    DB2 columns don't have a title like TD columns can.
    """

    column_element = C.Column(column_name, datatype, G.TABLE_STRUCTURE)

    column_element.naming_method, column_element.column_name_tokens = \
        split_name_parts(
            source='COLUMN',
            input_name=column_name,
            table_naming_method=G.TABLE_STRUCTURE.naming_method)

    column_element.position = len(G.TABLE_STRUCTURE.column_elements)

    column_element.is_identity = is_identity
    # There is not yet a rule against DB2 having an indentity, and the DB2
    # language supports identities, so I will leave this hear for now to
    # show where it would be set if people ever decide to.

    # -----------------------------------------------------------------------
    # We don't want to copy the whole Create Table command for each column.
    # But we can provide a little context from the lines
    # that referred to this column
    sql_stmt_txt = 'Column references\n'
    for line in G.TABLE_STRUCTURE.sql_stmt_txt.split('\n'):
        if re.search(column_name, line, re.IGNORECASE):
            sql_stmt_txt += line

    column_element.sql_stmt_txt = sql_stmt_txt

    if comment_txt is not None:
        comment_obj = C.ColumnComment(
            database_base_orig=G.TABLE_STRUCTURE.database_base_orig,
            table_name_orig=G.TABLE_STRUCTURE.table_name_orig,

            column_name_orig=column_name,
            comment_txt=comment_txt,
            input_filename=G.TABLE_STRUCTURE.input_filename,
            file_obj_list=G.INPUT_FILES)

        G.COLUMN_COMMENTS.append(comment_obj)

    # -----------------------------------------------------------------------
    G.TABLE_STRUCTURE.column_elements.append(column_element)


# ===============================================================================
def create_table_object(AA):
    """
    You might wonder - why can't we have a single consistent function to
    create the table object for all languages??
    Well, for example, Databricks doesn't have a command to set the
    default database.   Different languages create the table comments
    differently.    The languages are not consistent, so this job
    cannot be done consistently.   Ugh!!!
    """

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

    # The returned naming_method should be set to SNAKE_CASE
    # or MixedCase

    for column_descriptor in AA.column_descriptors:
        column_name, datatype = column_descriptor.split('|')

        add_db2_column_element(column_name, datatype,
                               comment_txt=None,
                               is_identity=False)

    G.TABLE_STRUCTURE.sql_stmt_obj = G.SQL_STATEMENT_OBJ
    G.TABLE_STRUCTURE.primary_key_is_specified = AA.primary_key_is_specified

    G.TABLE_STRUCTURES.append(G.TABLE_STRUCTURE)


# ===============================================================================
def display_sql_statement(AA):
    print_one_sql_statement(G.SQL_STATEMENT_OBJ)
    G.LOGGER.info('')
    indent(f'Tentative cmd: {AA.tentative_command_type}')
    indent(f'Command Type : {AA.statement_type}')

    if AA.statement_type in ('ALTER TABLE', 'CREATE TABLE', 'ALTER TABLE COLUMN'):
        indent(f'Schema Name  : {AA.database_base}')
        indent(f'Table Name   : {AA.table_name}')
    elif AA.statement_type == 'SET SCHEMA':
        indent(f'Schema Name  : {G.DATABASE_BASE_DEFAULT}')


# ===============================================================================
def get_db2_sql_statements_from_antlr_log(file_obj):
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

                create_sql_statement_obj(AA)

                if AA.statement_type in ('ALTER TABLE', 'CREATE TABLE', 'ALTER TABLE COLUMN'):
                    create_table_object(AA)

                display_sql_statement(AA)

                count_command_type(AA.statement_type)

                # Reinitialize the loop variables
                AA = C.AntlrAttributes(file_obj)

                G.SQL_STMT_NUM += 1

            elif re.search(r'Found database identifier    :', line):
                AA.database_base = split_value_from_line(line)

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
def get_db2_sql_statements_from_one_file(file_obj):
    # ---------------------------------------------------------------
    # Extract the SQL statements from each input file.

    sql_txt = get_file_contents(file_obj.input_filename)

    G.LOCAL_SCRIPT_NAME = write_local_script_name(sql_txt)

    ret = antlr_parse_stmt('DB2_115', G.LOCAL_SCRIPT_NAME)

    if ret == 0:
        get_db2_sql_statements_from_antlr_log(file_obj)


# ===============================================================================
def get_all_db2_sql_statements():
    G.LOGGER.info('Num Files to Process = {0}'.format(len(G.FILE_DICT)))
    G.LOGGER.info('Reading all DB2 files...')
    for G.FILE_NUM in range(len(G.FILE_DICT)):

        file_obj = G.INPUT_FILES[G.FILE_NUM]
        G.INPUT_FILENAME_REL = file_obj.input_filename_rel

        if file_obj.is_utf8_readable:
            get_db2_sql_statements_from_one_file(file_obj)
