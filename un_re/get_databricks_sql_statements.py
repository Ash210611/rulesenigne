# pylint: 	disable=C0209			# Don't require formatted strings.
# pylint: 	disable=R0912			# Allow more branches
# pylint: 	disable=R0915			# Allow more statements

import os
import re  # For re.search

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.antlr_parse_stmt import antlr_parse_stmt
from un_re.classify_command_type import classify_file_contents_with_regex
from un_re.count_command_type import count_command_type
from un_re.find_classword import find_classword
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.indent_info import indent_info
from un_re.print_command_summary import print_command_summary
from un_re.print_one_sql_statement import print_one_sql_statement
from un_re.rezero_the_command_counters import rezero_the_command_counters
from un_re.split_name_parts import split_name_parts
from un_re.split_value_from_line import split_value_from_line
from un_re.write_local_script_name import write_local_script_name


# ===============================================================================
# For other RULES_ENGINE_TYPEs, we split the SQL statements on a semi-colon
#
# For DATABRICKS, like DB2, and soon to be like Oracle, we will let Antlr 
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
def create_databricks_sql_statement_obj(AA):
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
def add_databricks_column_element(column_name, datatype, comment_txt, is_identity):
    '''
    Add this particular column instance

    This is tricky because a column element can be created either by
    a Create Table command or a Comment On command, and those commands could
    come in any order.

    Or it could be added by an Alter Table command.

    If the column element was previously added by a Comment On command,
    then we only need to update the attributes.

    Languages like Hive do not have Comment On commands.
    '''

    column_element = C.Column(column_name, datatype, G.TABLE_STRUCTURE)

    column_element.naming_method, column_element.column_name_tokens = \
        split_name_parts(
            source='COLUMN',
            input_name=column_name,
            table_naming_method=G.TABLE_STRUCTURE.naming_method)

    column_element.position = len(G.TABLE_STRUCTURE.column_elements)

    column_element.is_identity = is_identity

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
def create_table_object(AA, antlr_log):
    look_for_table_comment = False
    look_for_column_comment = False

    line = antlr_log.readline()
    while line != '':
        if re.search(r'Found database identifier    :', line):
            AA.database_base = split_value_from_line(line)
            G.DATABASE_BASE = AA.database_base

        elif re.search(r'Found table name             :', line):
            AA.table_name = split_value_from_line(line)

        elif re.search(r'Found primary key            :', line):
            AA.primary_key_is_specified = True

        elif re.search(r'Found column name            :', line):
            column_name = split_value_from_line(line)
            AC = C.AntlrColumn(column_name)
            AC.naming_method, AC.column_name_tokens = split_name_parts(
                source='COLUMN',
                input_name=column_name,
                table_naming_method='UNKNOWN')
            AC.classword = find_classword(
                AC.naming_method,
                AC.column_name_tokens)
            AA.column_descriptors.append(AC)

        elif re.search(r'  datatype                   :', line):
            datatype = split_value_from_line(line)
            datatype = datatype.upper()
            if datatype == 'INT':
                datatype = 'INTEGER'
            AC.datatype = datatype

        elif re.search(r'datatype_attribute.identity  : Found IDENTITY', line):
            # AC.datatype = 'IDENTITY'	# Usually an IDENTITY is a BIGINT
            AC.is_identity = True

        elif re.search(r'Found comment-on object      : TABLE', line):
            look_for_table_comment = True

        elif re.search(r'Found comment-on object      : COLUMN', line):
            look_for_column_comment = True

        elif re.search(r'Found comment-on string      :', line):
            if look_for_table_comment:
                table_comment = split_value_from_line(line)
                AA.table_comment = table_comment
                look_for_table_comment = False
            elif look_for_column_comment:
                column_comment = split_value_from_line(line)
                column_comment = re.sub(r'^COMMENT\s*', '', column_comment,
                                        flags=re.MULTILINE | re.IGNORECASE)

                column_comment = column_comment.strip("'")
                column_comment = column_comment.strip('"')
                # Databricks comments can be delimited
                # with either single or double quotes

                if AA.statement_type == 'COMMENT ON COLUMN':
                    AC.comment_txt = column_comment
                    AA.column_descriptors.append(AC)
                else:  # Like for the CREATE TABLE command
                    AC.comment_txt = column_comment
                    look_for_column_comment = False

        elif re.search(r'^Parsed single_statement      :', line):
            AA.read_sql_stmt_txt = True

        elif re.search(r'^End of parsed single stmt    :', line):
            AA.tentative_command_type = classify_file_contents_with_regex(AA.sql_stmt_txt)

            create_databricks_sql_statement_obj(AA)
            AA.read_sql_stmt_txt = False

            break

        elif AA.read_sql_stmt_txt:
            AA.sql_stmt_txt += line

        line = antlr_log.readline()

    if AA.database_base == 'UNKNOWN':
        if G.DATABASE_BASE is None:
            G.DATABASE_BASE = 'UNKNOWN'
        AA.database_base = G.DATABASE_BASE

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

    for AC in AA.column_descriptors:
        add_databricks_column_element(AC.column_name,
                                      AC.datatype,
                                      comment_txt=AC.comment_txt,
                                      is_identity=AC.is_identity)

    G.TABLE_STRUCTURE.sql_stmt_obj = G.SQL_STATEMENT_OBJ
    G.TABLE_STRUCTURE.primary_key_is_specified = AA.primary_key_is_specified

    G.TABLE_STRUCTURES.append(G.TABLE_STRUCTURE)

    if AA.table_comment is not None:
        if AA.database_base == 'UNKNOWN':
            if G.DATABASE_BASE is None:
                G.DATABASE_BASE = 'UNKNOWN'
            AA.database_base = G.DATABASE_BASE

        G.TABLE_COMMENT = C.TableComment(
            AA.database_base,
            AA.table_name,
            AA.table_comment,
            G.SQL_STATEMENT_OBJ)

        G.TABLE_COMMENTS.append(G.TABLE_COMMENT)

    return AA


# ===============================================================================
def create_table_comment_object(AA, antlr_log):
    look_for_table_comment = False

    line = antlr_log.readline()
    while line != '':
        if re.search(r'Found database identifier    :', line):
            AA.database_base = split_value_from_line(line)
            G.DATABASE_BASE = AA.database_base

        elif re.search(r'Found table name             :', line):
            AA.table_name = split_value_from_line(line)

        elif re.search(r'Found comment-on object      : TABLE', line):
            if look_for_table_comment:
                G.LOGGER.error('Unexpected condition.')
            else:
                look_for_table_comment = True

        elif re.search(r'Found comment-on string      :', line):
            if look_for_table_comment:
                table_comment = split_value_from_line(line)
                AA.table_comment = table_comment
                look_for_table_comment = False

        elif re.search(r'^Parsed single_statement      :', line):
            AA.read_sql_stmt_txt = True

        elif re.search(r'^End of parsed single stmt    :', line):
            AA.tentative_command_type = classify_file_contents_with_regex(AA.sql_stmt_txt)

            create_databricks_sql_statement_obj(AA)
            AA.read_sql_stmt_txt = False
            break

        elif AA.read_sql_stmt_txt:
            AA.sql_stmt_txt += line

        line = antlr_log.readline()

    if AA.database_base == 'UNKNOWN':
        if G.DATABASE_BASE is None:
            G.DATABASE_BASE = 'UNKNOWN'
        AA.database_base = G.DATABASE_BASE

    G.TABLE_COMMENT = C.TableComment(
        AA.database_base,
        AA.table_name,
        AA.table_comment,
        G.SQL_STATEMENT_OBJ)

    G.TABLE_COMMENTS.append(G.TABLE_COMMENT)

    return AA


# ===============================================================================
def add_comment_to_column(AA, antlr_log):
    """
    Call this function for the COMMENT ON COLUMN command, which is actually
    an Alter Table command.

    Can the Alter Table command add comments for more than one column??
    So far we only know of one.
    """

    look_for_column_comment = False

    line = antlr_log.readline()
    while line != '':
        if re.search(r'Found database identifier    :', line):
            AA.database_base = split_value_from_line(line)
            G.DATABASE_BASE = AA.database_base

        elif re.search(r'Found table name             :', line):
            AA.table_name = split_value_from_line(line)

        elif re.search(r'Found comment-on object      : COLUMN', line):
            if look_for_column_comment:
                G.LOGGER.error('Unexpected condition.')
            else:
                look_for_column_comment = True

        elif re.search(r'Found comment-on column name :', line):
            column_name = split_value_from_line(line)
            AC = C.AntlrColumn(column_name)
            AC.naming_method, AC.column_name_tokens = split_name_parts(
                source='COLUMN',
                input_name=column_name,
                table_naming_method='UNKNOWN')
            AC.classword = find_classword(
                AC.naming_method,
                AC.column_name_tokens)
            AA.column_descriptors.append(AC)

        elif re.search(r'Found comment-on string      :', line):
            if look_for_column_comment:
                column_comment = split_value_from_line(line)
                column_comment = re.sub(r'^COMMENT\s*', '', column_comment,
                                        flags=re.MULTILINE | re.IGNORECASE)

                column_comment = column_comment.strip("'")
                column_comment = column_comment.strip('"')
                # Databricks comments can be delimited
                # with either single or double quotes

                if AA.statement_type == 'COMMENT ON COLUMN':
                    AC.comment_txt = column_comment
                    AA.column_descriptors.append(AC)
                else:
                    G.LOGGER.error('Unexpected condition.')

        elif re.search(r'^Parsed single_statement      :', line):
            AA.read_sql_stmt_txt = True

        elif re.search(r'^End of parsed single stmt    :', line):
            AA.tentative_command_type = classify_file_contents_with_regex(AA.sql_stmt_txt)

            create_databricks_sql_statement_obj(AA)
            AA.read_sql_stmt_txt = False

            break

        elif AA.read_sql_stmt_txt:
            AA.sql_stmt_txt += line

        line = antlr_log.readline()

    AC = AA.column_descriptors[0]

    comment_obj = C.ColumnComment(
        database_base_orig=AA.database_base,
        table_name_orig=AA.table_name,

        column_name_orig=AC.column_name,
        comment_txt=AC.comment_txt,
        input_filename=AA.file_obj.input_filename,
        file_obj_list=G.INPUT_FILES)

    G.COLUMN_COMMENTS.append(comment_obj)

    return AA


# ===============================================================================
def create_optimize_object(AA, antlr_log):
    line = antlr_log.readline()
    while line != '':

        if re.search(r'Found database identifier    :', line):
            AA.database_base = split_value_from_line(line)
            G.DATABASE_BASE = AA.database_base

        elif re.search(r'Found table name             :', line):
            AA.table_name = split_value_from_line(line)

        elif re.search(r'Found column name            :', line):
            column_name = split_value_from_line(line)
            AC = C.AntlrColumn(column_name)
            AC.naming_method, AC.column_name_tokens = split_name_parts(
                source='COLUMN',
                input_name=column_name,
                table_naming_method='UNKNOWN')
            AC.classword = find_classword(
                AC.naming_method,
                AC.column_name_tokens)
            AA.column_descriptors.append(AC)

        elif re.search(r'^Parsed single_statement      :', line):
            AA.read_sql_stmt_txt = True

        elif re.search(r'^End of parsed single stmt    :', line):
            AA.tentative_command_type = classify_file_contents_with_regex(AA.sql_stmt_txt)

            create_databricks_sql_statement_obj(AA)
            AA.read_sql_stmt_txt = False
            break

        elif AA.read_sql_stmt_txt:
            AA.sql_stmt_txt += line

        line = antlr_log.readline()

    oo = C.DBXOptimizeStmt(
        database_base_orig=AA.database_base,
        table_name_orig=AA.table_name,
        zorder_columns=AA.column_descriptors,
        sql_obj=G.SQL_STATEMENT_OBJ,
        file_obj=AA.file_obj)

    G.DBX_OPTIMIZE_STMTS.append(oo)

    return AA


# ===============================================================================
def display_databricks_statement(AA):
    print_one_sql_statement(G.SQL_STATEMENT_OBJ)
    G.LOGGER.info('')
    indent(f'Tentative cmd: {AA.tentative_command_type}')
    indent(f'Command Type : {AA.statement_type}')

    if AA.statement_type in ('ALTER TABLE', 'CREATE TABLE',
                             'CREATE TABLE AS SELECT', 'OPTIMIZE'):

        indent(f'Schema Name  : {AA.database_base}')
        indent(f'Table Name   : {AA.table_name}')

    elif AA.statement_type == 'SET SCHEMA':
        indent(f'Schema Name  : {G.DATABASE_BASE}')


# ===============================================================================
def create_other_object(AA, antlr_log):
    line = antlr_log.readline()
    while line != '':

        if re.search(r'Found database identifier    :', line):
            AA.database_base = split_value_from_line(line)
            G.DATABASE_BASE = AA.database_base

        elif re.search(r'^Parsed single_statement      :', line):
            AA.read_sql_stmt_txt = True

        elif re.search(r'^End of parsed single stmt    :', line):
            AA.tentative_command_type = classify_file_contents_with_regex(AA.sql_stmt_txt)

            create_databricks_sql_statement_obj(AA)
            AA.read_sql_stmt_txt = False
            break

        elif AA.read_sql_stmt_txt:
            AA.sql_stmt_txt += line

        line = antlr_log.readline()

    return AA


# ===============================================================================
def get_databricks_sql_statements_from_antlr_log_2(file_obj):
    """
    This version _2 refactors the main loop to be smaller and use more
    support functions.   The old version of this function was over 130
    lines.  As more statement types were added, it was getting bigger and
    harder to maintain.   The smaller support functions will only focus on
    the lines they should expect, and then return to the loop here.
    """

    # SQL Statements are numbered within each file separately.
    G.SQL_STMT_NUM = 0

    # The following class will collect the various attributes we need to
    # observe from any SQL statement.
    AA = C.AntlrAttributes(file_obj)

    G.DATABASE_BASE = None

    rezero_the_command_counters()

    with open(G.ANTLR_LOG_FILENAME, 'rt', encoding='utf-8') as antlr_log:
        line = antlr_log.readline()
        while line != '':
            # A blank line would be '/n'
            # If line == '', we have reached the end of the file.

            if re.search(r'^Statement Type               :', line):
                AA.statement_type = split_value_from_line(line)

                if AA.statement_type in ('ALTER TABLE', 'CREATE TABLE', 'CREATE TABLE AS SELECT'):
                    AA = create_table_object(AA, antlr_log)
                elif AA.statement_type == 'OPTIMIZE':
                    AA = create_optimize_object(AA, antlr_log)
                elif AA.statement_type == 'COMMENT ON COLUMN':
                    AA = add_comment_to_column(AA, antlr_log)
                elif AA.statement_type == 'COMMENT ON TABLE':
                    AA = create_table_comment_object(AA, antlr_log)
                else:
                    AA = create_other_object(AA, antlr_log)

                G.SQL_STMT_NUM += 1
                display_databricks_statement(AA)

                count_command_type(AA.statement_type)

                # Reinitialize the loop variables
                AA = C.AntlrAttributes(file_obj)

            line = antlr_log.readline()

    G.LOGGER.info('')
    print_command_summary()


# ===============================================================================
# def get_databricks_sql_statements_from_antlr_log (file_obj):
# 	# This function is being refactored in the _2
#	# Delete this function after that is accepted.
# 
# 	# SQL Statements are numbered within each file separately.
# 	G.SQL_STMT_NUM		= 0
# 
# 	# The following class will collect the various attributes we need to
# 	# observe from any SQL statement.
# 	AA = C.AntlrAttributes (file_obj)
# 
# 	G.DATABASE_BASE		= None
# 
# 	rezero_the_command_counters ()
# 	look_for_table_comment = False
# 	look_for_column_comment = False
# 
# 	with open (G.ANTLR_LOG_FILENAME, 'rt', encoding='utf-8') as antlr_log:
# 		for line in antlr_log.readlines ():
# 
# 			if re.search (r'^Statement Type               :', line):
# 				AA.statement_type = split_value_from_line (line)
# 
# 			elif re.search (r'^Parsed single_statement      :', line):
# 				AA.read_sql_stmt_txt = True
# 
# 			elif re.search (r'^End of parsed single stmt    :', line):
# 				AA.tentative_command_type = classify_file_contents_with_regex (AA.sql_stmt_txt)
# 
# 				create_databricks_sql_statement_obj (AA)
# 
# 				if AA.statement_type in ('ALTER TABLE', 'CREATE TABLE', 'CREATE TABLE AS SELECT'):
# 					create_table_object (AA)
# 				elif AA.statement_type == 'COMMENT ON TABLE':
# 					create_table_comment_object (AA)
# 				elif AA.statement_type == 'COMMENT ON COLUMN':
# 					add_comment_to_column (AA)
# 				elif AA.statement_type == 'OPTIMIZE':
# 					create_optimize_object (AA)	
# 
# 				display_databricks_statement (AA)
# 
# 				count_command_type (AA.statement_type)
# 
# 				# Reinitialize the loop variables
# 				AA = C.AntlrAttributes (file_obj)
# 				G.SQL_STMT_NUM += 1
# 				
# 			elif re.search (r'Found database identifier    :', line):
# 				AA.database_base = split_value_from_line (line)
# 				G.DATABASE_BASE = AA.database_base
# 
# 			elif re.search (r'Found table name             :', line):
# 				AA.table_name = split_value_from_line (line)
# 
# 			elif re.search (r'Found primary key            :', line):
# 				AA.primary_key_is_specified = True
# 
# 			# elif re.search (r'Found default schema         :', line):
# 			#	G.DATABASE_BASE_DEFAULT = split_value_from_line (line)
# 
# 			elif re.search (r'Found column name            :', line):
# 				column_name = split_value_from_line (line)
# 				AC = C.AntlrColumn (column_name)
# 				AC.naming_method, AC.column_name_tokens = split_name_parts (
# 	                                source = 'COLUMN',
# 	                                input_name = column_name,
# 	                                table_naming_method = 'UNKNOWN')
# 				AC.classword = find_classword (
#                                                         AC.naming_method,
#                                                         AC.column_name_tokens)
# 				AA.column_descriptors.append (AC)
# 
# 			elif re.search (r'Found comment-on column name :', line):
# 				column_name = split_value_from_line (line)
# 				AC = C.AntlrColumn (column_name)
# 				AC.naming_method, AC.column_name_tokens = split_name_parts (
# 	                                source = 'COLUMN',
# 	                                input_name = column_name,
# 	                                table_naming_method = 'UNKNOWN')
# 				AC.classword = find_classword (
#                                                         AC.naming_method,
#                                                         AC.column_name_tokens)
# 				AA.column_descriptors.append (AC)
# 
# 			elif re.search (r'  datatype                   :', line):
# 				datatype = split_value_from_line (line)
# 				datatype = datatype.upper ()
# 				if datatype == 'INT':
# 					datatype = 'INTEGER'
# 				AC.datatype = datatype
# 
# 			elif re.search (r'Found comment-on object      : TABLE', line):
# 				if look_for_table_comment:
# 					G.LOGGER.error ('Unexpected condition.')
# 				else:
# 					look_for_table_comment = True
# 
# 			elif re.search (r'Found comment-on object      : COLUMN', line):
# 				if look_for_column_comment:
# 					G.LOGGER.error ('Unexpected condition.')
# 				else:
# 					look_for_column_comment = True
# 
# 			elif re.search (r'Found comment-on string      :', line):
# 				if look_for_table_comment:
# 					table_comment = split_value_from_line (line)
# 					AA.table_comment = table_comment
# 					look_for_table_comment = False
# 				elif look_for_column_comment:
# 					column_comment = split_value_from_line (line)
# 					column_comment = re.sub (r'^COMMENT\s*', '', column_comment, 
# 								flags=re.MULTILINE | re.IGNORECASE)
# 
# 					column_comment = column_comment.strip ("'")
# 					column_comment = column_comment.strip ('"')
# 					# Databricks comments can be delimited 
# 					# with either single or double quotes
# 
# 					if AA.statement_type == 'COMMENT ON COLUMN':
# 						AC.comment_txt = column_comment
# 						AA.column_descriptors.append (AC)
# 					else:		# Like for the CREATE TABLE command
# 						AC.comment_txt = column_comment
# 					look_for_column_comment = False
# 				else:
# 					G.LOGGER.error ('Unexpected condition.')
# 			elif re.search (r'datatype_attribute.identity  : Found IDENTITY', line):
# 				# AC.datatype = 'IDENTITY'	# Usually an IDENTITY is a BIGINT
# 				AC.is_identity = True
# 
# 			elif AA.read_sql_stmt_txt:
# 				AA.sql_stmt_txt += line
# 
# 	G.LOGGER.info ('')
# 	print_command_summary ()
# 
# ===============================================================================
def clean_databricks_sql_txt(sql_txt):
    # Change um_${env}.rxa_um_cnfz.um_clncl_eoc_save_rpt;
    # To     um_env.rxa_um_cnfz.um_clncl_eoc_save_rpt;
    regex1 = r'\${(.[^}]*?)}'
    matches = re.finditer(regex1, sql_txt, re.MULTILINE)
    found_match = False
    for matchNum, match in enumerate(matches, start=1):
        found_match = True
        indent("Match {matchNum} found at {start}-{end}: {match}".format(
            matchNum=matchNum,
            start=match.start(),
            end=match.end(),
            match=match.group()))
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1

            indent("Group {groupNum} found at {start}-{end}: {group}".format(
                groupNum=groupNum,
                start=match.start(groupNum),
                end=match.end(groupNum),
                group=match.group(groupNum)))

    if found_match:
        subst = "\\1"
        sql_txt = re.sub(regex1, subst, sql_txt, 99, re.MULTILINE)

    return sql_txt


# ===============================================================================
def databricks_extract_from_py(file_obj):
    """
    We want to keep the Python file, and put the SQL statements into a new
    file.
    """

    file_contents = get_file_contents(file_obj.input_filename)

    # remove Python comments
    file_contents = re.sub(r'\#.*$', '', file_contents, 0, re.MULTILINE)

    file_contents = clean_databricks_sql_txt(file_contents)

    regex = r'''spark\.sql\s?\([fr]*[\"\']+(.*?)[\"\']+\).*$'''
    matches = re.finditer(regex, file_contents, re.MULTILINE)

    temp_sql_statements = []
    for _, match in enumerate(matches, start=1):
        # _ is the matchnum

        # print ("Match {matchNum} was found at {start}-{end}: {match}".format(
        #	matchNum = matchNum, start = match.start(),
        #	end = match.end(), match = match.group()))

        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1

            # print ("Group {groupNum} found at {start}-{end}: {group}".format(
            #	groupNum = groupNum, start = match.start(groupNum),
            #	end = match.end(groupNum), group = match.group(groupNum)))

            start = match.start(groupNum)
            end = match.end(groupNum)
            stmt = file_contents[start:end]
            stmt = stmt.strip()
            temp_sql_statements.append(stmt)

    block_of_sql = ''
    for i, stmt in enumerate(temp_sql_statements):
        block_of_sql += f'/* {i} */ {stmt};\n'

    file_obj.input_filename_rel += ".sql"
    G.INPUT_FILENAME_REL = file_obj.input_filename_rel
    G.LOCAL_SCRIPT_NAME = write_local_script_name(block_of_sql)

    ret = antlr_parse_stmt('DATABRICKS', G.LOCAL_SCRIPT_NAME)

    if ret == 0:
        get_databricks_sql_statements_from_antlr_log_2(file_obj)


# ===============================================================================
def databricks_extract_from_sql(file_obj):
    file_contents = get_file_contents(file_obj.input_filename)

    file_contents = clean_databricks_sql_txt(file_contents)

    G.LOCAL_SCRIPT_NAME = write_local_script_name(file_contents)

    ret = antlr_parse_stmt('DATABRICKS', G.LOCAL_SCRIPT_NAME)

    if ret == 0:
        get_databricks_sql_statements_from_antlr_log_2(file_obj)


# ===============================================================================
def get_databricks_sql_statements_from_one_file(file_obj):
    """
    Extract the SQL statements from each input file.
    """

    _, file_extension = os.path.splitext(file_obj.input_filename_rel)

    if re.search(r'\.py', file_extension, re.IGNORECASE):
        databricks_extract_from_py(file_obj)

    elif re.search(r'\.sql', file_extension, re.IGNORECASE):
        databricks_extract_from_sql(file_obj)


# ===============================================================================
def get_databricks_sql_statements():
    G.LOGGER.info('Num Files to Process = {0}'.format(len(G.FILE_DICT)))
    G.LOGGER.info('Reading all DATABRICKS files...')
    for G.FILE_NUM in range(len(G.FILE_DICT)):

        file_obj = G.INPUT_FILES[G.FILE_NUM]
        G.INPUT_FILENAME_REL = file_obj.input_filename_rel

        G.LOGGER.info('')
        indent_info('=' * 72)
        indent_info('Filenum, name: {0}, {1}'.format(
            G.FILE_NUM + 1,
            G.INPUT_FILENAME_REL))

        if file_obj.is_utf8_readable:
            get_databricks_sql_statements_from_one_file(file_obj)
