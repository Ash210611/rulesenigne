import os
import re
import sys

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G
from un_re.dreml_extract_from_BTEQ import dreml_extract_from_BTEQ
from un_re.dreml_extract_from_ksh import dreml_extract_from_ksh
from un_re.dreml_extract_from_py import dreml_extract_from_py
from un_re.dreml_extract_from_txt import dreml_extract_from_txt
from un_re.extract_sql_stmts_from_sql_file import extract_sql_stmts_from_sql_file


# ===============================================================================
def dreml_extract_sql_stmts(file_num, inp_filename):
    _, file_extension = os.path.splitext(inp_filename)

    # print ('file_extension={0}'.format (file_extension))

    if re.search(r'\.py', file_extension, re.IGNORECASE):
        sql_statements = dreml_extract_from_py(inp_filename)

    elif re.search(r'\.sql', file_extension, re.IGNORECASE):
        sql_statements = extract_sql_stmts_from_sql_file(inp_filename)

    elif re.search(r'\.ksh', file_extension, re.IGNORECASE):
        sql_statements = dreml_extract_from_ksh(inp_filename)

    elif re.search(r'\.BTEQ', file_extension, re.IGNORECASE):
        sql_statements = dreml_extract_from_BTEQ(inp_filename)

    elif re.search(r'\.txt', file_extension, re.IGNORECASE):
        sql_statements = dreml_extract_from_txt(file_num, inp_filename)

    else:
        G.LOGGER.error('Unknown extension.')
        sys.exit(E.UNKNOWN_EXTENSION)

    return sql_statements
