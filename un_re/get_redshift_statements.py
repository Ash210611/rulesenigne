# pylint:	disable=C0209			# Don't require formatted strings

import glob
import re

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.check_g012 import check_g012
from un_re.check_r416 import check_r416
from un_re.classify_command_type import classify_input_filename_command_type
from un_re.clean_database_base import clean_database_base
from un_re.count_command_type import count_command_type
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.indent_error import indent_error
from un_re.notice_file_findings import notice_file_findings
from un_re.print_command_summary import print_command_summary
from un_re.print_msg import print_msg
from un_re.rezero_the_command_counters import rezero_the_command_counters
from un_re.set_database_num import set_database_num
from un_re.split_db_from_obj_name import split_db_from_obj_name
from un_re.split_name_parts import split_name_parts
from un_re.split_value_from_line import split_value_from_line


# ===============================================================================
def read_other_statement():
    G.OTHER_STATEMENT = C.OtherStatement(G.SQL_STMT_NUM, G.SQL_STATEMENT,
                                         G.COMMAND_TYPE, G.INPUT_FILENAME,
                                         G.INPUT_FILENAME_REL, G.INPUT_FILES)

    G.OTHER_STATEMENTS.append(G.OTHER_STATEMENT)


# ===============================================================================
def read_comment_on_column():
    '''
    Load the results from Antler syntax analysis into the class objects
    '''

    table_name = None  # yet.
    column_name = None  # yet.
    column_comment = None  # yet.

    for line in G.ANTLR_LOG_CONTENTS.split('\n'):

        if re.search(r'Found comment-on object      :', line, re.IGNORECASE):

            value = split_value_from_line(line.upper())
            num_dots = value.count('.')
            if num_dots == 1:
                table_name = value.split('.')[0]
                column_name = value.split('.')[1]
            elif num_dots == 2:
                G.DATABASE_BASE = clean_database_base(value.split('.')[0])
                table_name = value.split('.')[1]
                column_name = value.split('.')[2]
            # else??

            if G.DATABASE_BASE == '':
                G.DATABASE_BASE = 'UNKNOWN'

            # Check if we already have an object for this column comment.
            # During deployment, the last one wins!
            found_it = False
            for column_comment in G.COLUMN_COMMENTS:
                if column_comment.database_base_upper == G.DATABASE_BASE and \
                        column_comment.table_name_upper == table_name and \
                        column_comment.column_name_upper == column_name.upper():
                    found_it = True
                    break

            if not found_it:
                column_comment = C.ColumnComment(
                    G.DATABASE_BASE,
                    table_name,
                    column_name,
                    None,  # comment_txt will be on the next line
                    G.INPUT_FILENAME,
                    G.INPUT_FILES)

                G.COLUMN_COMMENTS.append(column_comment)

        if re.search(r'Found comment-on string      :', line, re.IGNORECASE):
            comment_txt = split_value_from_line(line)
            comment_txt = comment_txt.strip("'")

            column_comment.comment_txt = comment_txt
            return


# ===============================================================================
def read_comment_on_table():
    '''
    Load the results from Antler syntax analysis into the class objects
    '''

    for line in G.ANTLR_LOG_CONTENTS.split('\n'):

        if re.search(r'Found comment-on object      :', line, re.IGNORECASE):

            G.TABLE_NAME = split_value_from_line(line.upper())

            if G.TABLE_NAME.find('.') > -1:
                G.DATABASE_BASE, G.TABLE_NAME = split_db_from_obj_name(G.TABLE_NAME)

            G.TABLE_COMMENT = C.TableComment(
                G.DATABASE_BASE,
                G.TABLE_NAME,
                None,  # Will be updated next
                G.SQL_STATEMENT_OBJ)

            G.TABLE_COMMENTS.append(G.TABLE_COMMENT)

            continue

        if re.search(r'Found comment-on string      :', line, re.IGNORECASE):
            comment = split_value_from_line(line)
            comment = comment.strip("'")

            # G.LOGGER.debug ('Comment = "{0}"'.format (comment))
            # G.LOGGER.debug ('Len comment = {0}'.format (len (comment)))
            G.TABLE_COMMENT.comment_txt = comment
            return


# ===============================================================================
def read_foreign_key_references():
    foreign_key_action = ''
    for line in G.ANTLR_LOG_CONTENTS.split('\n'):

        if re.search(r'Found AT Add Foreign Key     : ', line, re.IGNORECASE):

            foreign_key_action = 'ADD'

        elif re.search(r'Found AT Drop Foreign Key    : ', line, re.IGNORECASE):
            foreign_key_action = 'DROP'

        elif re.search(r'Foreign key references       : ', line, re.IGNORECASE):

            if foreign_key_action == 'ADD' or \
                    G.TABLE_STRUCTURE.command_type == 'CREATE TABLE':
                foreign_key_reference = split_value_from_line(line.upper())

                G.TABLE_STRUCTURE.foreign_key_clauses.append(foreign_key_reference)

                if G.VERBOSE:
                    G.LOGGER.debug('References   : {0}'.format(foreign_key_reference))


# ===============================================================================
def create_table_structure(table_name_orig, found_redshift_distkey):
    G.TABLE_STRUCTURE = C.RedshiftTableStructure(
        G.DATABASE_BASE,
        table_name_orig,
        G.SQL_STATEMENT_OBJ)

    G.TABLE_STRUCTURES.append(G.TABLE_STRUCTURE)
    G.REDSHIFT_TABLE_STRUCTURES = G.TABLE_STRUCTURES

    if found_redshift_distkey:
        G.TABLE_STRUCTURE.set_distkey(found_redshift_distkey, G.DISTKEY_COLUMN)

    G.TABLE_STRUCTURE.naming_method, G.TABLE_STRUCTURE.table_name_tokens = \
        split_name_parts(
            source='TABLE',
            input_name=G.TABLE_STRUCTURE.table_name_orig,
            table_naming_method='UNKNOWN')

    # The returned naming_method should be set to SNAKE_CASE
    # or MixedCase

    return G.TABLE_STRUCTURE


# ===============================================================================
def check_for_redshift_distkey(line, found_redshift_distkey):
    if re.search(r'Found table distribution key        : ', line, re.IGNORECASE):
        found_redshift_distkey = True
    elif re.search(r'Found table distribution key alt1       : ', line, re.IGNORECASE):
        found_redshift_distkey = True
        G.DISTKEY_COLUMN = 'DEFAULT'
    if re.search(r'Found table distribution key column name       : ', line, re.IGNORECASE):
        distkey_column = split_value_from_line(line)
        distkey_column = distkey_column.strip('"')
        distkey_column = distkey_column.strip("'")
        G.DISTKEY_COLUMN = distkey_column

    return found_redshift_distkey


# ===============================================================================
def read_create_table():
    '''
    A Create Table command may or may not specify the database.  If the
    database is not specified, the table would be created in the default
    database.

    The default database needs to be specified at least once in the input
    file, but it could have been specified by a USE Database command, or a
    default databsae command.

    For that reason, the Antlr grammar files need to be sure to print the
    database identifier before they print the table name.
    '''

    # Hive syntax puts the table comment in the Create Table command
    found_redshift_distkey = False
    G.TABLE_STRUCTURE = None

    for line in G.ANTLR_LOG_CONTENTS.split('\n'):
        if G.RULES_ENGINE_TYPE == 'REDSHIFT':
            found_redshift_distkey = check_for_redshift_distkey(
                line, found_redshift_distkey)

        if re.search(r'Found database identifier    : ', line, re.IGNORECASE):
            G.DATABASE_BASE = split_value_from_line(line.upper())
            G.DATABASE_BASE = clean_database_base(G.DATABASE_BASE)
            set_database_num()

        elif re.search(r'Found table name             :', line, re.IGNORECASE):

            G.TABLE_NAME = split_value_from_line(line)
            G.TABLE_NAME = G.TABLE_NAME.strip('`')

            if G.TABLE_NAME.find('.') > -1:
                G.DATABASE_BASE, G.TABLE_NAME = split_db_from_obj_name(G.TABLE_NAME)

            if G.DATABASE_BASE == '':
                G.DATABASE_BASE = 'UNKNOWN'

            G.TABLE_STRUCTURE = create_table_structure(G.TABLE_NAME, found_redshift_distkey)

    if G.VERBOSE:
        G.LOGGER.debug('Database Base: {0}'.format(G.DATABASE_BASE))
        G.LOGGER.debug('Table Name   : {0}'.format(G.TABLE_STRUCTURE.table_name_orig))
        G.LOGGER.debug('Naming Method: {0}'.format(G.TABLE_STRUCTURE.naming_method))

    read_foreign_key_references()

    return 0


# ===============================================================================
def read_create_view():
    '''
    Note that the Create View command does not set a default database
    context.

    And, at Cigna, we require views to explicitly specify the target
    database for where to create the view, and not take it from the
    default database context.

    For that reason, the database for the view is initialized as UNKNOWN
    '''

    view_database_base = 'UNKNOWN'

    for line in G.ANTLR_LOG_CONTENTS.split('\n'):

        if re.search(r'Found database identifier    : ', line, re.IGNORECASE):
            view_database_base = split_value_from_line(line.upper())
            view_database_base = clean_database_base(view_database_base)

        elif re.search(r'Found view name              :', line, re.IGNORECASE):

            G.VIEW_NAME = split_value_from_line(line.upper())

            found_view_structure = False

            for G.VIEW_STRUCTURE in G.VIEW_STRUCTURES:

                if G.VIEW_STRUCTURE.database_base_upper == view_database_base and \
                        G.VIEW_STRUCTURE.view_name_upper == G.VIEW_NAME:
                    found_view_structure = True
                    break

            if found_view_structure:
                G.VIEW_STRUCTURE.sql_statement = G.SQL_STATEMENT
                G.VIEW_STRUCTURE.sql_stmt_num = G.SQL_STMT_NUM

            else:

                G.VIEW_STRUCTURE = C.ViewStructure(view_database_base,
                                                   G.VIEW_NAME,
                                                   G.SQL_STATEMENT_OBJ)

                G.VIEW_STRUCTURES.append(G.VIEW_STRUCTURE)

    if G.VERBOSE:
        G.LOGGER.debug('Database Base: {0}'.format(view_database_base))
        G.LOGGER.debug('View Name    : {0}'.format(G.VIEW_NAME))

    return 0


# ===============================================================================
def update_column_attributes(column_element, datatype):
    was_updated = False

    if datatype is None and G.COMMAND_TYPE == 'ALTER TABLE COLUMN':
        # The table might be being updated, but not the datatype.
        # Return True so the column is not added twice.
        was_updated = True

    elif datatype != '' and column_element.datatype is None:
        # Then it was previously added by a Comment On
        # command, or maybe by an Alter Table command,
        # So update the datatype now.
        column_element.datatype = datatype

        print('Updated column element datatype for {0}.{1}.{2}'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper,
            column_element.name_upper))

        was_updated = True

    return was_updated


# ===============================================================================
def add_redshift_column_element(name, datatype, is_identity):
    '''
    DB2 columns don't have a title like TD columns do
    '''

    for column_element in G.TABLE_STRUCTURE.column_elements:
        if name.upper() == column_element.name_upper:
            # If the column name matches, update the attributes if
            # possible, and return.  Do not add the column twice.

            was_updated = update_column_attributes(column_element, datatype)

            if was_updated:
                print('was updated')
                return

    # Add this particular column instance

    column_element = C.Column(name, datatype, G.TABLE_STRUCTURE)

    column_element.naming_method, column_element.column_name_tokens = \
        split_name_parts(
            source='COLUMN',
            input_name=column_element.name_orig,
            table_naming_method=G.TABLE_STRUCTURE.naming_method)

    column_element.position = len(G.TABLE_STRUCTURE.column_elements)

    column_element.is_identity = is_identity

    # -----------------------------------------------------------------------
    # We don't want to copy the whole Create Table command for each column.
    # But we can provide a little context from the lines
    # that referred to this column
    sql_stmt_txt = 'Column references\n'
    for line in G.TABLE_STRUCTURE.sql_stmt_txt.split('\n'):
        if re.search(name, line, re.IGNORECASE):
            sql_stmt_txt += line

    column_element.sql_stmt_txt = sql_stmt_txt

    # -----------------------------------------------------------------------
    G.TABLE_STRUCTURE.column_elements.append(column_element)


# ===============================================================================
def read_column_elements():
    '''
    This can be tricky.  Because of the way output from Antlr is logged
    from the bottom-up, it might report some details before displaying
    the column name they belong to.
    '''

    name = ''
    datatype = None
    is_identity = False

    # The following 2 flags are needed because it is unpredictable whether
    # a datatype_len or a datatype_attribute will be found
    column_is_added = False
    column_should_be_added = False

    # G.TABLE_STRUCTURE.column_elements = []
    # It should already be initialized like that, so that should not be necessary

    for line in G.ANTLR_LOG_CONTENTS.split('\n'):
        if line.find('[@') > -1:
            continue

        if re.search(r'Found column_name            :', line):
            if column_should_be_added and not column_is_added:
                add_redshift_column_element(name, datatype, is_identity)
                datatype = None
                is_identity = False

            name = split_value_from_line(line)

            name = name.strip("`")
            # I don't know why they wrap column names in a back tick,
            # but sometimes they do.

            column_is_added = False
            column_should_be_added = True

        elif re.search(r'datatype_attribute.identity  : Found IDENTITY', line):
            datatype = 'IDENTITY'
            is_identity = True

        elif re.search(r'  datatype                   :', line):
            if datatype != 'IDENTITY':
                datatype = split_value_from_line(line)
                datatype = datatype.upper()

        elif re.search(r'  Found column distkey       :', line):
            G.TABLE_STRUCTURE.distkey = True
            G.TABLE_STRUCTURE.distkey_column = name

        elif re.search(r'  datatype_len               :', line):
            datatype_len = split_value_from_line(line)

            # At this point, we know all 3 things - the column
            # name, the data type, and the length, if any.
            datatype = '{0}{1}'.format(
                datatype,
                datatype_len)
            datatype = datatype.upper()

            add_redshift_column_element(name, datatype, is_identity)
            is_identity = False

            column_is_added = True
            column_should_be_added = False

        elif re.search(r'  datatype_attribute         :', line):
            # Some data types have a datatype_len, and some don't
            # If we see the attribute, and have not seen the len yet,
            # Then it is one of those, and we need to check it now.

            if not column_is_added:
                add_redshift_column_element(name, datatype, is_identity)
                datatype = None
                is_identity = False

                column_is_added = True
                column_should_be_added = False

    # Remember to write the last one.
    if column_should_be_added and not column_is_added:
        add_redshift_column_element(name, datatype, is_identity)


# ===============================================================================
def read_default_database():
    '''
    The default database is not saved in a class object, because it is
    just a single attribute with no attributes.

    It is sufficient to save the default database in G.DATABASE_BASE

    Knowing the default database is important for setting the context of
    other commands
    '''

    for line in G.ANTLR_LOG_CONTENTS.split('\n'):

        if re.search(r'Found database identifier    : ', line, re.IGNORECASE):
            G.DATABASE_BASE = split_value_from_line(line).upper()
            G.DATABASE_BASE = clean_database_base(G.DATABASE_BASE)
            set_database_num()

    if G.DATABASE_BASE == '':
        print_msg('WARNING-g004 : No Database Base was found in this command.')
        indent('The default database must be set with a command, and not in a comment.')

    if G.VERBOSE:
        G.LOGGER.debug('Database Base: {0}'.format(G.DATABASE_BASE))


# ===============================================================================
def get_sql_statement_obj(antlr_log_filename):
    '''
    This function will populate the SQL_Statement class object,
    regardless of the command type.

    This is useful for scanning ETL files, which can contain all kinds
    of command types.

    A typical antlr_filename will be:
        check_g002.sql.00019.sql.antlr.re.log
    '''

    sql_filename = antlr_log_filename.replace('.antlr.re.log', '')
    # sql_stmt_txt = get_file_contents (sql_filename).rstrip ('\n')

    sql_num_filename = sql_filename.replace('.sql', '')
    sql_num = sql_num_filename.split('.')[-1]
    G.SQL_STMT_NUM = int(sql_num) - 1

    for sql_stmt_obj in G.SQL_STATEMENT_OBJS:
        if sql_stmt_obj.antlr_log_filename == antlr_log_filename:
            return sql_stmt_obj

    G.LOGGER.error('Error: Uh-oh, cannot find sql_stmt_obj with this antlr_log_filename:')
    G.LOGGER.error(f'       {antlr_log_filename}')
    G.LOGGER.error('The available antlr_log_filenames are:')
    for i, sql_stmt_obj in enumerate(G.SQL_STATEMENT_OBJS):
        indent_error(f'{i}: {sql_stmt_obj.antlr_log_filename}')

    return None


# ===============================================================================
def get_redshift_findings(antlr_log_filename):
    G.ANTLR_LOG_CONTENTS = get_file_contents(antlr_log_filename)

    classify_input_filename_command_type(antlr_log_filename)

    G.LOGGER.debug('Command type : {0}'.format(G.COMMAND_TYPE))
    count_command_type(G.COMMAND_TYPE)

    G.SQL_STATEMENT_OBJ = get_sql_statement_obj(antlr_log_filename)

    if G.SQL_STATEMENT_OBJ is None:
        # Something went wrong.
        # Inspect the diagnostics.
        return

    G.SQL_STATEMENT_OBJ.command_type = G.COMMAND_TYPE

    if G.COMMAND_TYPE in (
            'CREATE TABLE',
            'CREATE TABLE AS SELECT'):
        read_create_table()

    if G.COMMAND_TYPE == 'CREATE TABLE':

        # CTAS statements don't have column elements

        read_column_elements()

    elif G.COMMAND_TYPE == 'DEFAULT DATABASE':

        read_default_database()

    elif G.COMMAND_TYPE == 'CREATE VIEW':

        read_create_view()

    elif G.COMMAND_TYPE in ('INSERT', 'GRANT'):

        read_other_statement()

    elif G.COMMAND_TYPE == 'COMMENT ON COLUMN':

        read_comment_on_column()

    elif G.COMMAND_TYPE == 'COMMENT ON TABLE':

        read_comment_on_table()

    return


# ===============================================================================
def get_redshift_statements_from_1_file(file_num):
    G.FILE_OBJ = G.INPUT_FILES[file_num]
    wildcard_spec = G.TEMP_DIR + '/' + G.INPUT_FILENAME_REL + '.*.antlr.re.log'

    antlr_log_filenames = sorted(glob.glob(wildcard_spec))

    num_antlr_log_filenames = len(antlr_log_filenames)
    found_a_failure = False

    for i in range(num_antlr_log_filenames):
        G.ANTLR_LOG_FILENAME = antlr_log_filenames[i]

        if G.VERBOSE:
            G.LOGGER.debug('')
            G.LOGGER.debug('Filename     : {0}'.format(G.ANTLR_LOG_FILENAME.replace(
                G.TEMP_DIR + '/', '$TEMP_DIR' + '/')))

        if found_a_failure:
            if G.VERBOSE:
                G.LOGGER.debug('Antlr status : Skipped.')
                continue

        elif re.search(r'failed.antlr.re.log', G.ANTLR_LOG_FILENAME):
            found_a_failure = True
            if G.VERBOSE:
                G.LOGGER.debug('Antlr status : Failed with a syntax error.')

                G.FILE_OBJ.has_a_syntax_error = True
                # Must set that flag again, because it is not
                # saved during the antlr_parse_stmt phase that
                # runs in parallel child processes
                continue

        G.ANTLR_LOG_CONTENTS = get_file_contents(G.ANTLR_LOG_FILENAME)

        if re.search(r'Antlr syntax check succeeded.', G.ANTLR_LOG_CONTENTS):
            get_redshift_findings(G.ANTLR_LOG_FILENAME)

        else:
            G.RULE_ID = 'g003'

            this_filename = G.ANTLR_LOG_FILENAME.replace(G.TEMP_DIR + '/', '')
            this_filename = this_filename.replace('.sql.skipped.antlr.re.log', '')

            print_msg('Notice-{0}  : Failed to check {1}.'.format(
                G.RULE_ID,
                this_filename))
            notice_file_findings(G.INPUT_FILENAME)

            G.INPUT_FILES[file_num].has_a_syntax_error = True


# ===============================================================================
def get_redshift_statements():
    '''
    Now that the input files have been parsed, load their findings
    from the Antlr log files into the class objects

    This function will loop through all input filenames, and statements
    from each file, and call the get_antlr_findings function for each one.
    '''

    G.LOGGER.info('Reading results from the Antlr syntax-parsing step...')

    for G.FILE_NUM in range(len(G.FILE_DICT)):
        G.LOGGER.info('=' * 88)
        G.LOGGER.info('File Number  = {0}.'.format(
            G.FILE_NUM + 1))

        if not G.INPUT_FILES[G.FILE_NUM].is_utf8_readable:
            continue

        rezero_the_command_counters()

        G.INPUT_FILENAME_REL = G.FILE_DICT[G.FILE_NUM]

        G.INPUT_FILENAME = G.INPUT_DIR + '/' + G.FILE_DICT[G.FILE_NUM]

        # Check rules that apply to the whole filename here
        if 'r416' in G.SHOULD_CHECK_RULE:
            check_r416(G.INPUT_FILENAME)  # no control characters
        if 'g012' in G.SHOULD_CHECK_RULE:
            check_g012(G.INPUT_FILENAME)  # valid ruleset indicator

        get_redshift_statements_from_1_file(G.FILE_NUM)

        print_command_summary()

    G.LOGGER.info('Done reading results from the Antlr syntax-parsing step.')
    return 0