# pylint:	disable=C0209		# Don't require formatted strings
# pylint: 	disable=R0912		# Too many branches
# pylint: 	disable=R0915		# Too many statements

import os
import re
from typing import List

import un_re.global_shared_variables as G
from un_re.get_file_contents import get_file_contents
from un_re.remove_comments import remove_comments


# ===============================================================================
def replace_bind_variables(sql_statement: str) -> str:
    sql_statement = sql_statement.replace('?', 'Something')
    # G.LOGGER.debug ( sql_statement )

    return sql_statement


# ===============================================================================
def pg_re_sql_setup(file_contents: str) -> str:
    # Temporarily add a semi-colon to any slash commands
    new_contents = ''
    for line in file_contents.split('\n'):
        if re.search(r'^\\', line):
            line = line + ';'

        new_contents += (line + '\n')
    if file_contents != new_contents:
        file_contents = new_contents

    # Remove the unnecessary COPY slash data
    in_copy = False
    new_contents = ''

    for line in file_contents.split('\n'):
        if not in_copy:
            new_contents += (line + '\n')

        elif re.search(r'^\\\.', line):
            in_copy = False

        if re.search(r'^COPY', line):
            in_copy = True
        # We added the line that says COPY, and will add
        # no more until we see the \.

    if file_contents != new_contents:
        file_contents = new_contents

    return file_contents


# ===============================================================================
def pg_re_sql_closeup(sql_statement: str) -> str:
    # Remove any semi-colons temporarily added to slash commands
    if re.search(r'^\\', sql_statement):
        sql_statement = sql_statement.rstrip(';')

    return sql_statement


# ===============================================================================
def extract_sql_stmts_from_sql_file(inp_filename: str) -> List[str]:
    '''
    Extract the SQL statements from a .sql file.

        This function will return a list of sql statements in a Python [] list.

    The DDL Rules Engine does a similar thing, but it puts the SQL
    statements into split files, while this puts them into a Python list.

        The input filename is expected to have an extension of SQL or TXT.
        If other extensions start to be used, add a branch to include those.
    '''

    G.RULE_ID = 'g002'

    _, file_extension = os.path.splitext(inp_filename)

    if re.search(r'\.sql', file_extension, re.IGNORECASE) or \
            re.search(r'\.hql', file_extension, re.IGNORECASE) or \
            re.search(r'\.txt', file_extension, re.IGNORECASE):

        pass  # keep going

    else:
        G.LOGGER.info('Skipping this file - Unknown extension.')
        return []

    # =======================================================================
    file_contents = get_file_contents(inp_filename)

    if G.RULES_ENGINE_TYPE == 'PG_RE':
        file_contents = pg_re_sql_setup(file_contents)

    # =======================================================================
    # Initialize some variables used inside the loop
    prev_ch1 = ''
    prev_ch2 = ''
    in_a_line_comment = False
    in_a_block_comment = False
    in_a_single_quoted_string = False
    in_a_double_quoted_string = False
    sql_statements = []
    sql_statement = ''

    for ch in file_contents:

        if ch == '?':
            # Replace bind parameters, unless they are
            # inside quoted strings

            if in_a_line_comment or \
                    in_a_block_comment or \
                    in_a_single_quoted_string or \
                    in_a_double_quoted_string:

                sql_statement += ch

            else:
                sql_statement += 'Bind_Parameter'

        else:
            sql_statement += ch

        if in_a_line_comment:
            if ch == '\n':
                in_a_line_comment = False

        elif in_a_block_comment:
            if prev_ch1 == r'*' and ch == r'/':
                in_a_block_comment = False

        elif in_a_single_quoted_string:
            # This sequence of checking the if-then-else
            # conditions is deliberate.  Just because you
            # read a semicolon does not mean the statement
            # is complete, because it can have a semicolon
            # inside a comment string.

            # Also check the prev_ch1 to escaped single quotes
            # For example found in:
            # REGEXP_REPLACE(UPPER(PPDM.FRST_NM),'[^-0-9A-ZA-Z\' &,./]+', '')
            if ch == "'":
                if prev_ch1 == '\\':
                    if prev_ch2 == "'":
                        # For example, a Teradata UESCAPE string,
                        # '\'
                        in_a_single_quoted_string = False
                    else:
                        pass

                elif not in_a_double_quoted_string:
                    in_a_single_quoted_string = False

        elif in_a_double_quoted_string:
            if ch == '"':
                # print ('Prev_ch = {0}, ch = {1}'.format (prev_ch1, ch))
                if prev_ch1 == '\\' and prev_ch2 != '\\':
                    # The double-quote is escaped.
                    # Caution! Hive has the option to specify
                    # a variable escape character, so hard-coding
                    # this is limited.
                    # print ('passed')
                    pass
                elif not in_a_single_quoted_string:
                    # print ('closing string')
                    in_a_double_quoted_string = False

        elif ch == '-' and prev_ch1 == '-':
            in_a_line_comment = True
        # Don't split the text because of a semi-colon in a line comment

        elif ch == r'*' and prev_ch1 == r'/':
            in_a_block_comment = True
        # Don't split the text because of a semi-colon in a block comment

        elif ch == "'":
            if not in_a_double_quoted_string:
                in_a_single_quoted_string = True

        elif ch == '"':
            if not in_a_single_quoted_string:
                in_a_double_quoted_string = True

        elif ch == ';':
            # Only close this statement and open another if
            # not in a line comment, a block comment, or a
            # quoted string

            sql_statement = remove_comments(sql_statement)
            sql_statement = sql_statement.strip(' \t\n\r')

            # sql_statement = replace_bind_variables (sql_statement)
            # Do not replace bind parameters inside quotes
            # This is checked and handled above.

            if len(sql_statement) > 1:

                if G.RULES_ENGINE_TYPE == 'PG_RE':
                    sql_statement = pg_re_sql_closeup(sql_statement)

                sql_statements.append(sql_statement)
            sql_statement = ''

        prev_ch2 = prev_ch1
        prev_ch1 = ch

    sql_statement = remove_comments(sql_statement)
    sql_statement = sql_statement.strip(' \t\n\r')

    sql_statement_len = len(sql_statement)
    if sql_statement_len > 1:
        sql_statement = sql_statement + '\n/* UN_RE appended missing semi-colon here */ ;'
        sql_statements.append(sql_statement)

    return sql_statements
