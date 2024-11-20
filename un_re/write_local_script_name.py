# pylint: disable=C0209			# Don't require formatted strings
import os

import un_re.global_shared_variables as G

from un_re.fprint import fprint
from un_re.make_local_script_dir import make_local_script_dir


# ===============================================================================
def write_local_script_name(sql_statement: str, stmt_num: int = None) -> str:
    '''
    This function writes the current SQL statement into a local
    (temporary) folder, so that it can scanned without touching the
    original input file

    It is important to be able to work from a copy of the original file
    so that shell-variable substitutions can satisfy SQL syntax without
    changing the original
    '''

    # Write the current SQL statement into a file
    # for Antlr to analyze.
    if stmt_num is None:
        G.LOCAL_SCRIPT_NAME = G.TEMP_DIR + '/' + '{0}'.format(
            G.INPUT_FILENAME_REL)
    else:
        G.LOCAL_SCRIPT_NAME = G.TEMP_DIR + '/' + '{0}.{1:05d}.sql'.format(
            G.INPUT_FILENAME_REL, stmt_num + 1)

    # Note that by formatting the stmt_num as 05d, we are allowing 10,000
    # SQL statements per file.  Hopefully that is enough.  The benefit of
    # formatting the filename that is that sorting the filenames
    # alphabetically will also sort them numerically in the order
    # they were written in the file, which will be needed later
    # to call the get_antlr_findings function in the right order.

    G.LOCAL_SCRIPT_NAME = G.LOCAL_SCRIPT_NAME.replace(' ', '_')

    local_script_dir = os.path.dirname(G.LOCAL_SCRIPT_NAME)

    make_local_script_dir(local_script_dir)

    with open(G.LOCAL_SCRIPT_NAME, "w", encoding='utf-8') as sql_file:
        fprint(sql_file, sql_statement)

    return G.LOCAL_SCRIPT_NAME
