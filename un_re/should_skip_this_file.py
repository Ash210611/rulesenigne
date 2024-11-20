import re

import un_re.global_shared_variables as G


# ===============================================================================
def should_skip_this_file(full_filename):
    '''
    Return true if this filename is on the list of filenames to skip
    Return false otherwise.
    '''
    for exc_filename in G.EXC_FILENAME_LIST:
        if re.search(exc_filename, full_filename):
            location = full_filename.replace(G.WORKSPACE, '$WORKSPACE')
            G.LOGGER.info(f'Ignoring excepted file: {location}')
            return True  # This file is on the list to be skipped.

    return False  # Do not skip this file.
