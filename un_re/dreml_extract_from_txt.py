import re

import un_re.global_shared_variables as G
from un_re.extract_sql_stmts_from_sql_file import extract_sql_stmts_from_sql_file
from un_re.get_file_contents import get_file_contents


# ===============================================================================
def dreml_extract_from_txt(file_num, inp_filename):
    """
    Txt files are usually the same as SQL files.

    Sometimes txt files contain data or QA tests rather than SQL.

    If no SQL is found, the file will be skipped.

    If we see 4 pipe symbols in a row, this is probably a data file rather
    than a SQL statement.
    """

    file_contents = get_file_contents(inp_filename)
    if re.search(r'\|\|\|\|', file_contents, re.MULTILINE):
        G.LOGGER.info(f'File {file_num + 1} has 4 consecutive pipe symbols, probably not SQL')
        return []

    if not re.search(';', file_contents, re.MULTILINE):
        G.LOGGER.info(f'File {file_num + 1} has no semi-colon, probably not SQL')
        return []

    if re.search(r'!\|Query\|', file_contents, re.IGNORECASE | re.MULTILINE):
        G.LOGGER.info(f'File {file_num + 1} looks like a Fitnesse test file, probably not SQL.')
        return []

    return extract_sql_stmts_from_sql_file(inp_filename)
