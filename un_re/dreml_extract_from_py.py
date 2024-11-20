# pylint: disable=R0912			# Too many branches
# pylint: disable=R0915			# Too many statements
# pylint: disable=R0902			# Too many instance attributes
# pylint: disable=C0209			# Don't require formatted strings

import os  # for basename
import re  # for re.search

from antlr4 import CommonTokenStream  # type: ignore
from antlr4 import FileStream  # type: ignore

import un_re.global_shared_variables as G
from un_re.Antlr.Python3Lexer import Python3Lexer  # type: ignore
from un_re.indent_error import indent_error
from un_re.print_msg import print_msg
from un_re.print_msg import report_firm_finding
from un_re.remove_comments import remove_comments


# ===============================================================================
def format_token(tok):
    token = str(tok)
    # To start with, a token will look like this:
    # [@933,11047:11064='base_ref_cd_attrib',<70>,294:12]

    is_a_channel = False

    # Remove tokens sent to the hidden channel
    if token.find(',channel=1,') > -1:

        is_a_channel = True

    else:
        # Take the part after the first equals sign.
        token = token.split('=', 1)[1]

        # Reverse the string to prepare for the next operation
        token = token[::-1]

        # The token looks like this now:
        # ]21:813,>07<,'birtta_dc_fer_esab'

        # Take the part after the second comma
        token = token.split(',', 2)[2]

        # Reverse the string back to normal
        token = token[::-1]

        # Remove the trailing single quote from the token
        token = token[:-1]

        # Remove the starting single quote from the token
        token = token[1:]

    # Uncomment this for debugging purposes
    # G.LOGGER.info (token)

    return is_a_channel, token


# ===============================================================================
def format_token_string(token):
    token_is_a_string = False
    if token.find('"""') > -1:
        # remove the triple double quotes
        token = token[:-3]
        token = token[3:]

        token_is_a_string = True

    elif token.find("'''") > -1:
        # remove the triple single quotes
        token = token[:-3]
        token = token[3:]

        token_is_a_string = True

    elif token.find('"') > -1:
        # remove the enclosing double quotes
        token = token[:-1]
        token = token[1:]

        token_is_a_string = True

    elif token.find("'") > -1:
        # remove the enclosing single quotes
        token = token[:-1]
        token = token[1:]

        token_is_a_string = True

    return token_is_a_string, token


# ===============================================================================
def assemble_string_fragments(T):
    if T.prev_token[0] == '=':
        # Assignments are not continuations of previous strings.
        # Assignments start a new string, but don't simply skip them.
        T.full_string = ''

    elif T.prev_token[3] == 'ccw' and \
            T.prev_token[2] == '.' and \
            T.prev_token[1] == 'Statement' and \
            T.prev_token[0] == '(':
        # The ccw.Statement function wraps new SQL statements.
        T.full_string = ''

    # Replace newline strings with real newlines
    T.token = T.token.replace('\\n', '\n')

    # Replace tabs with real tabs
    T.token = T.token.replace('\\t', '\t')

    if T.passed_doc_string:
        if T.token[0] == '.':
            # If the string fragment starts with a dot,
            # the intervening chunk was likely a DB qualifier.
            T.full_string += 'Some_DB'

        elif T.prev_token_type[0] == 'plus sign' and \
                T.prev_token_type[1] == 'unknown' and \
                T.prev_token_type[2] == 'plus sign':

            T.full_string += 'Something'

        # handle this kind of statement:
        # statement = "sel count(*) from " + tbl_nm + " ;")

        T.full_string += T.token
        # print (f'full_string = {full_string}\n\n')
        # Debug eqe_lab_lz_member_match_p1.py

        if T.token.find(';') > -1:
            if re.search(r'<html>', T.full_string, re.IGNORECASE | re.MULTILINE):
                T.sql_statements.append(T.full_string)
            # HTML styles include lots of semicolons.
            # HTML is going to be identified later to be skipped anyway.
            else:
                T.full_string = remove_comments(T.full_string)
                for sql_statement in T.full_string.split(';'):
                    if len(sql_statement) > 0:
                        T.sql_statements.append(sql_statement + ';')
                    # restoring the semicolon removes by split

            T.full_string = ''

    return T


# ===============================================================================
def handle_string_token(T):
    if T.prev_token[0] == '[':
        # This token is an array index, not a SQL statement or fragment
        pass

    elif T.prev_token[0] == 'print':
        # This is a print string, not a SQL statement or fragment
        T.full_string = ''

    elif T.prev_token[1] == 'print':
        # This is a print string, inside print()
        # Skip this too.
        T.full_string = ''

    elif T.prev_token[1] == 'info':
        # This is a call to the logger.info function.
        # Skip this too.
        T.full_string = ''

    elif T.prev_token[0] == ',':
        # For example:
        #   with open(file_nm, 'rb') as csvfile:
        # or
        #   log.create(os.path.basename(sys.argv[0]),'debug',log_path='/logs/py_logs/reference/phrmrds/')
        T.full_string = ''

    else:
        # This still qualifies as a SQL statement or fragment
        T = assemble_string_fragments(T)

    return T


# ===============================================================================
class Token_Context:
    def __init__(self):
        self.token = ''
        self.prev_token = ['', '', '', '']

        self.sql_statements = []  # List of stmts to return

        self.string_num = 0  # Count how many strings found.

        self.ina_def_or_class = False
        self.passed_doc_string = False
        self.passed_colon = False
        self.full_string = ''

        self.token_type = ''  # type of the current token
        self.prev_token_type = ['', '', '']

    def __hash__(self):
        return hash(self.token)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
def dreml_extract_from_py(inp_filename):
    """
    This function will parse an input filename in the Python language.
    Then it will read through the list of tokens parsed from that file,
    identify which ones look like SQL statements, and return the list
    of SQL statements to the caller for further processing and analysis.

    If we have a def or class, then we must pass a colon, then pass an
    equal sign before we can safely decide we have passed the doc string.

    if we are not in a def or class, then we don't need to pass a colon,
    only an equal sign before we can safely decide we have passed the
    doc string.
    """

    try:
        lexer = Python3Lexer(FileStream(inp_filename))

    except UnicodeDecodeError as err:
        G.RULE_ID = 'g001'

        report_firm_finding(
            object_type_nm='FILE',
            object_nm=G.INPUT_FILENAME,
            severity='ERROR',
            message='A Unicode Decode error occurred while trying to read {0}'.format(
                inp_filename.replace(G.WORKSPACE + '/', '')),
            class_object=G.INPUT_FILES[G.FILE_NUM])

        G.INPUT_FILES[G.FILE_NUM].is_utf8_readable = False

        G.LOGGER.error('')
        indent_error(str(err))
        G.LOGGER.error('')
        indent_error('Either remove the unexpected character, or')
        indent_error('skip that file by listing its name in the DREML_files_to_skip.lst file.')
        return []

    token_stream = CommonTokenStream(lexer)

    try:
        token_stream.fill()
    except:

        G.RULE_ID = 'g003'

        print_msg('{0}-g003 : Something is invalid about this Python file: {1}.'.format(
            G.RULES[G.RULE_ID].severity,
            os.path.basename(G.INPUT_FILENAME)))
        indent_error('Either adjust the syntax to be valid for Python, or')
        indent_error('skip that file by listing its name in the DREML_files_to_skip.lst file.')

        for file_obj in G.INPUT_FILES:
            if file_obj.input_filename_rel == G.INPUT_FILENAME_REL:
                # Mark it now to be reported later by the
                # check_g003 function.
                file_obj.has_a_syntax_error = True
                break
        return []

    T = Token_Context()

    for tok in token_stream.tokens:
        (is_a_channel, T.token) = format_token(tok)

        if is_a_channel:
            continue

        # G.LOGGER.info ('token = {0}'.format (token))

        if T.token in ('def', 'class'):
            T.ina_def_or_class = True
            T.passed_doc_string = False
            T.passed_colon = False

            # G.LOGGER.info ('passed_doc_string = False')

            T.full_string = ''
            # Because no string from the previous function would
            # concatenate to a string in this function

        if T.token == ':':
            # The class or def specification is complete.
            # It is not enough to simply look for the first equal
            # sign to indicate the doc string is passed, because
            # defaults can be assigned to input parameters using an
            # equals sign in the function specification.
            T.passed_colon = True

        if T.token == '=':
            if T.ina_def_or_class:
                if T.passed_colon:
                    # It is important to distinguish doc strings
                    # from other quoted strings.
                    # After we see a class or def specifier, we
                    # must pass both a colon, and an equal sign
                    # before we can trust that the doc string is passed.

                    T.passed_doc_string = True
                    # G.LOGGER.info ('passed_doc_string = True')
                    # Reset the other flags False now
                    T.ina_def_or_class = False
                    T.passed_colon = False
            else:
                T.passed_doc_string = True
                T.ina_def_or_class = False
                T.passed_colon = False

        (token_is_a_string, T.token) = format_token_string(T.token)

        if token_is_a_string:
            T.token_type = 'string'
            T.string_num += 1

            if len(T.token) == 0:
                # for example:
                # header_format_remove_space = ''.join(header_format.split())
                token_is_a_string = False

        elif T.token == '+':
            T.token_type = 'plus sign'
        else:
            T.token_type = 'unknown'

        # print ('token = {0}'.format (token))

        if token_is_a_string:
            T = handle_string_token(T)

        T.prev_token_type[2] = T.prev_token_type[1]
        T.prev_token_type[1] = T.prev_token_type[0]
        T.prev_token_type[0] = T.token_type

        T.prev_token[3] = T.prev_token[2]
        T.prev_token[2] = T.prev_token[1]
        T.prev_token[1] = T.prev_token[0]
        T.prev_token[0] = T.token

    return T.sql_statements
