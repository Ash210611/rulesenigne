# pylint: disable=W0702				# Allow bare except blocks

import os  # for dirname
import re

import un_re.global_shared_variables as G
from un_re.extract_sql_stmts_from_sql_file import extract_sql_stmts_from_sql_file
from un_re.make_local_script_dir import make_local_script_dir


# from	un_re.indent				import indent


# ===============================================================================
def get_eof_marker(line):
    """
    Given a line like this:
        bteq << !EOF_LOAD

    return !EOF_LOAD
    """

    line = line.split(r'<<')[1]
    line = line.strip(' \t\n\r')

    line = line.split(' ')[0]  # Split away anything after the marker
    line = line.strip(' \t\n\r')

    return line


# ===============================================================================
def extract_sql_block(sql_block):
    sql_filename = G.TEMP_DIR + '/' + G.INPUT_FILENAME_REL + '.sql'

    # Make sure the target directory exists.
    sql_filename_dir = os.path.dirname(sql_filename)
    make_local_script_dir(sql_filename_dir)

    with open(sql_filename, "w", encoding='utf-8') as sql_file:
        sql_file.write(sql_block)

    tmp_sql_statements = extract_sql_stmts_from_sql_file(sql_filename)

    # except:
    #	print_msg ('Failed to write the extract sql block.  Must skip.')

    return tmp_sql_statements


# ===============================================================================
def dreml_extract_from_ksh(inp_filename):
    """
    This function will parse an input filename in the ksh format.

    It is expected that SQL statements in a ksh script will be found
    in a here script that calls bteq.    In other words, the SQL statements
    follow the bteq command, and continue to the end of the here script.

    Lines with dot directives will be ignored, especially since those do
    not need to be terminated with semicolons.

    Those guidelines will extract the block of SQL statements.   Individual
    SQL statements need to be terminated with semicolons though, and
    separating those is tricky, because a semicolon might be inside a
    quoted string or a comment.   So, put the SQL block into a temp file
    and call the function to parse the SQL block from that file.
    """

    # if G.VERBOSE:
    # 	indent ('Reading file  : {0}...'.format (
    #		os.path.basename (inp_filename)))

    sql_statements = []  # List of stmts to return

    in_bteq_block = False
    eof_marker = ''
    sql_block = ''

    # compile the regex outside the loop
    # We have a ? after the asterisk to change the regex from greedy to lazy.
    dollar_dot = re.compile(r'\$.*?\.', re.MULTILINE)
    dollar_curly = re.compile(r'\${.*?}', re.MULTILINE)
    dollar_quoted = re.compile(r"'\$.*?'", re.MULTILINE)
    dollar_semi = re.compile(r"\$.*?;", re.MULTILINE)

    # \w is any word character
    # \w+ matches one or more word characters
    # \w+\s matches one or more word characters followed by a space
    dollar_space = re.compile(r"\$\w+\s", re.MULTILINE)

    dollar_eol = re.compile(r'\$.*$', re.MULTILINE)

    with open(inp_filename, 'r', encoding='utf-8') as f:
        for line in f.readlines():

            if in_bteq_block:

                # Replace shell variables following by a dot with something.
                line = dollar_dot.sub('Dollar_Dot.', line)
                line = dollar_curly.sub('Dollar_Curly', line)
                line = dollar_quoted.sub("'Dollar_Quote'", line)
                line = dollar_semi.sub('Dollar_Semi;', line)

                line = dollar_space.sub('Dollar_Space ', line)

                line = dollar_eol.sub('Dollar_Eol', line)

                if line.find(eof_marker) > -1:
                    in_bteq_block = False
                    eof_marker = ''

                    # print ('sql_block = {0}'.format (sql_block))
                    tmp_sql_statements = extract_sql_block(sql_block)
                    sql_statements += tmp_sql_statements

                elif re.search(r'^\.', line):
                    # Ignore dot directive lines
                    # G.LOGGER.debug ( 'Ignoring: {0}'.format (line) )
                    pass

                elif re.search('^SET.*QUERY_BAND', line, re.IGNORECASE):
                    # Also ignore set directives.
                    pass

                else:
                    sql_block += line

            if line.find('bteq') > -1:
                try:
                    eof_marker = get_eof_marker(line)
                    in_bteq_block = True
                # print ('eof_marker = {0}'.format (eof_marker))
                except:
                    pass
                # Apparently it is not actually a bteq block

    # print (sql_statements)

    return sql_statements
