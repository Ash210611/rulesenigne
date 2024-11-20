import os
import re

import un_re.global_shared_variables as G
from un_re.get_file_contents import get_file_contents


# ===============================================================================
def count_stmts_processed():
    num_processed = 0
    num_total = 0

    # for subdir, dirs, files in os.walk...
    for subdir, _, files in os.walk(G.TEMP_DIR):
        for this_file in sorted(files):
            filename = subdir + os.sep + this_file

            if re.search(r'.sql.(skipped.|failed.)?antlr.re.log', filename, re.IGNORECASE):

                num_total += 1

                file_contents = get_file_contents(filename)

                for line in file_contents.split('\n'):
                    if re.search(r'Antlr syntax check succeeded.', line):
                        num_processed += 1

    return num_processed, num_total
