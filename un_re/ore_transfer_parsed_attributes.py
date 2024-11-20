# pylint: disable=C0209             # Don't require formtted strings

import re

import un_re.class_definitions as C
import un_re.global_shared_variables as G

from un_re.find_classword import find_classword
from un_re.split_name_parts import split_name_parts
from un_re.split_value_from_line import split_value_from_line
from un_re.split_db_from_obj_name import split_db_from_obj_name

from un_re.indent_debug import indent_debug


# ===============================================================================
def transfer_grant_attributes(sql_stmt_obj):
    '''
    This function transfers the attributes specific to GRANT commands,
    namely, the grantee and the permission that was granted.
    '''

    grant_stmt_obj = C.GrantStatementObj(sql_stmt_obj)
    G.GRANT_STATEMENTS.append(grant_stmt_obj)

    for line in sql_stmt_obj.antlr_log_contents.split('\n'):
        if re.search('Granted permission           : ', line):
            grant_stmt_obj.granted_permission = split_value_from_line(line)

        elif re.search('Grantee                      : ', line):
            grant_stmt_obj.grantee = split_value_from_line(line)


# ===============================================================================
def find_index_name(sql_stmt_obj):
    G.DATABASE_NAME = 'UNKNOWN'
    index_name_orig = 'UNKNOWN'

    for line in sql_stmt_obj.antlr_log_contents.split('\n'):

        if re.search(r'Found database identifier    : ', line, re.IGNORECASE):
            G.DATABASE_BASE = split_value_from_line(line.upper())

        elif re.search(r'Found index name             :', line, re.IGNORECASE):

            index_name_orig = split_value_from_line(line)
            index_name_orig = index_name_orig.strip('`')

            if index_name_orig.find('.') > -1:
                G.DATABASE_BASE, index_name_orig = split_db_from_obj_name(index_name_orig)

    return G.DATABASE_BASE, index_name_orig


# ===============================================================================
def match_or_create_index_obj(sql_stmt_obj, index_name_orig):
    # Check if we have already created a structure for this table
    found_index_obj = False
    for G.INDEX_OBJ in G.INDEX_OBJS:

        if G.INDEX_OBJ.database_base_upper == G.DATABASE_BASE and \
                G.INDEX_OBJ.index_name_upper == index_name_orig.upper():
            found_index_obj = True
            break

    if found_index_obj:
        if sql_stmt_obj.command_type == 'CREATE INDEX':
            G.INDEX_OBJ.sql_statement = sql_stmt_obj.sql_stmt_txt
            G.INDEX_OBJ.sql_stmt_num = sql_stmt_obj.sql_stmt_num

    # indent_debug ('Updating existing index object.')
    else:
        # indent_debug ('Creating a new index object.')

        new_index_obj = C.Index_Obj(
            G.DATABASE_BASE,
            index_name_orig,
            sql_stmt_obj)

        G.INDEX_OBJ = new_index_obj
        G.INDEX_OBJS.append(new_index_obj)

    return G.INDEX_OBJ


# ===============================================================================
def transfer_create_index_attributes(sql_stmt_obj):
    '''
    An index could come from a Create Index command, or an Alter Table
    Constraint command. Both cases will contain the keyword INDEX in the
    command somewhere.
    '''

    G.INDEX_OBJ = None

    if not re.search('INDEX', sql_stmt_obj.sql_stmt_txt, re.IGNORECASE):
        return

    G.DATABASE_BASE, index_name_orig = find_index_name(sql_stmt_obj)

    if index_name_orig == 'UNKNOWN' and \
            sql_stmt_obj.command_type == 'ALTER TABLE CONSTRAINT':

        # Rescan and use the constraint name for the name of the index.
        for line in sql_stmt_obj.antlr_log_contents.split('\n'):
            if re.search(r'  Constraint name            : ', line, re.IGNORECASE):
                index_name_orig = split_value_from_line(line)
                indent_debug('Constraint Nm: {0}'.format(index_name_orig))

    if index_name_orig != 'UNKNOWN':

        G.INDEX_OBJ = match_or_create_index_obj(sql_stmt_obj, index_name_orig)

        # Now that we have an index obj, get the name(s) of the
        # tablespaces.
        for line in sql_stmt_obj.antlr_log_contents.split('\n'):
            if re.search(r'  Index tablespace name    ', line, re.IGNORECASE):
                tablespace_name = split_value_from_line(line)
                G.INDEX_OBJ.tablespaces.append(tablespace_name)

        if G.VERBOSE:
            indent_debug('Database Base: {0}'.format(G.DATABASE_BASE))
            indent_debug('Index Name   : {0}'.format(G.INDEX_OBJ.index_name_orig))

    elif G.VERBOSE:
        indent_debug('Index Name   : {0}'.format(index_name_orig))


# ===============================================================================
def create_table_obj(sql_stmt_obj, table_name_orig):
    if G.DATABASE_BASE == '':
        G.DATABASE_BASE = 'UNKNOWN'

    new_table_structure = C.TableStructure(
        G.DATABASE_BASE,
        table_name_orig,
        sql_stmt_obj)

    new_table_structure.naming_method, new_table_structure.table_name_tokens = \
        split_name_parts(
            source='TABLE',
            input_name=table_name_orig,
            table_naming_method='UNKNOWN')

    G.TABLE_STRUCTURE = new_table_structure
    G.TABLE_STRUCTURES.append(new_table_structure)

    return G.TABLE_STRUCTURE


# ===============================================================================
def transfer_create_table_attributes(sql_stmt_obj):
    '''
    A Create Table command may or may not specify the database.  If the
    database is not specified, the table would be created in the default
    database.

    For that reason, the Antlr grammar files need to be sure to print the
    database identifier before they print the table name.
    '''

    G.TABLE_STRUCTURE = None

    for line in sql_stmt_obj.antlr_log_contents.split('\n'):

        if re.search(r'Found database identifier    : ', line, re.IGNORECASE):
            G.DATABASE_BASE = split_value_from_line(line.upper())

        elif re.search(r'Found table name             :', line, re.IGNORECASE):

            table_name_orig = split_value_from_line(line)
            table_name_orig = table_name_orig.strip('`')

            if table_name_orig.find('.') > -1:
                G.DATABASE_BASE, table_name_orig = split_db_from_obj_name(table_name_orig)

            G.TABLE_STRUCTURE = create_table_obj(sql_stmt_obj, table_name_orig)

        elif re.search(r'  Primary key is specified.', line, re.IGNORECASE):
            G.TABLE_STRUCTURE.primary_key_is_specified = True

        elif re.search(r'  Tablespace_name          ', line, re.IGNORECASE):
            tablespace_name = split_value_from_line(line)
            G.TABLE_STRUCTURE.tablespaces.append(tablespace_name)

    if G.VERBOSE:
        indent_debug('Database Base: {0}'.format(G.DATABASE_BASE))
        indent_debug('Table Name   : {0}'.format(G.TABLE_STRUCTURE.table_name_orig))

    return G.TABLE_STRUCTURE


# ===============================================================================
def add_column_element(name, datatype, table_obj):
    column_element = C.Column(name, datatype, table_obj)

    column_element.naming_method, column_element.column_name_tokens = split_name_parts(
        source='COLUMN',
        input_name=name,
        table_naming_method='UNKNOWN')

    column_element.classword = find_classword(
        column_element.naming_method,
        column_element.column_name_tokens)

    column_element.position = len(table_obj.column_elements)

    table_obj.column_elements.append(column_element)


# ===============================================================================
def transfer_column_elements(sql_stmt_obj, table_obj):
    '''
    A column name might be empty for an Alter Table DROP column command.
    '''

    name = ''
    datatype = ''

    # G.TABLE_STRUCTURE.column_elements = []
    # It should already be initialized like that, so that should not be necessary

    for line in sql_stmt_obj.antlr_log_contents.split('\n'):
        if line.find('[@') > -1:
            continue

        if re.search(r'Found column_name            : ', line):

            datatype = ''
            name = split_value_from_line(line)

        elif re.search(r'  datatype                   :', line):
            datatype = split_value_from_line(line)
            datatype = datatype.upper()

            if name != '':
                add_column_element(name, datatype, table_obj)

            name = ''
            datatype = ''

    # Remember to write the last one.
    if name != '':
        add_column_element(name, datatype, table_obj)


# ===============================================================================
def ore_transfer_parsed_attributes(sql_stmt_obj):
    '''
    This function will transfer the parsed attributes from the Antlr log
    contents into the class objects.

    After this transfer, it is straightforward to write code for a rule thta
    will check the class object attributes to see if they meet the Cigna
    standards.

    Different types of commands have different attributes, so the different
    attributes are transferred with different helper functions.
    '''

    if sql_stmt_obj.command_type == 'GRANT':

        transfer_grant_attributes(sql_stmt_obj)

    elif sql_stmt_obj.command_type == 'CREATE INDEX':

        transfer_create_index_attributes(sql_stmt_obj)

    elif sql_stmt_obj.command_type in ('CREATE TABLE',
                                       'ALTER TABLE COLUMN'):

        table_obj = transfer_create_table_attributes(sql_stmt_obj)

        transfer_column_elements(sql_stmt_obj, table_obj)

    elif sql_stmt_obj.command_type == 'ALTER TABLE CONSTRAINT':

        transfer_create_table_attributes(sql_stmt_obj)

        # If they are adding a primary key, we need to add that
        # attribute to a table object.  If the PK is supported
        # by an index, we also need to add it to an index object.
        transfer_create_index_attributes(sql_stmt_obj)

# Parse more statement types here.
# For example, parse the Alter Table command
