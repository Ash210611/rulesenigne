import os
import sys

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G
from un_re.print_msg import print_msg


# ===============================================================================
def check_file_size(filename):
    statinfo = os.stat(filename)

    max_size = 750 * 1024
    # 1 MB has proven too big for Python 3.6

    if statinfo.st_size > max_size:
        print_msg('ERROR: File size too big!')
        G.LOGGER.error(f'This file is {statinfo.st_size} bytes.')
        G.LOGGER.error('Python 3.6 crashes with a memory error when files are too big.')
        G.LOGGER.error('Please reduce the size below {max_size} bytes, and retry.')

        sys.exit(E.FILE_TOO_BIG)
