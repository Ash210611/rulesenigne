import sys

import un_re.global_shared_variables as G
from un_re.indent import indent


# ======== ========= ========= ========= ========= ========= ========= ==========
def check_for_dup_include_files():
    """
    Check for duplicate filenames in the list of include files.

    Will exit the whole procedure if any are found.
    """

    indent('Checking the xml file for duplicate filenames...')

    sorted_files_to_process = sorted(G.FILE_DICT.values())
    previous_filename = ''
    found_one = False
    for this_filename in sorted_files_to_process:
        if this_filename == previous_filename:
            G.LOGGER.error('')
            G.LOGGER.error('ERROR:         A duplicate filename was found in the XML file.')
            G.LOGGER.error(f'Dup filename:  {this_filename}')
            found_one = True
        previous_filename = this_filename

    if found_one:
        G.LOGGER.error('Please remove the duplicates and retry.')
        G.LOGGER.error('')
        sys.exit(103)
