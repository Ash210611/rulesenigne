# pylint: disable=C0209           # Don't require formtted strings

import os
import re
import sys

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.fprint import fprint
from un_re.print_msg import print_msg
from un_re.should_skip_this_file import should_skip_this_file


# ===============================================================================
def damodre_file_should_be_scanned(full_filename):
    """
    Check if this file should be scanned.
    Different kinds of files have different acceptance criteria.
    """

    # Skip subdirectories, because those are not filenames.
    if os.path.isdir(full_filename):
        return False

    # If the path says do not use, then don't!
    if full_filename.find('do_not_use') > -1:
        return False

    if should_skip_this_file(full_filename):
        return False

    if re.search(r'.sql$', full_filename, re.IGNORECASE):
        return True

    if re.search(r'.txt$', full_filename, re.IGNORECASE):
        return True

    # else:	# Skip all other file types
    return False


# ===============================================================================
def damodre_get_full_list_of_input_files():
    filenum = 0
    num_files_checked = 0
    # for subdir, dirs, files in os.walk(G.INPUT_DIR):
    for subdir, _, files in os.walk(G.INPUT_DIR):
        for this_file in sorted(files):
            G.INPUT_FILENAME = subdir + os.sep + this_file

            if G.INPUT_FILENAME.find('do_not_use') > -1:
                pass  # Skip files on this path.

            elif G.INPUT_FILENAME.find('site-packages') > -1:
                pass  # Skip files on this path.

            else:
                num_files_checked += 1
                if damodre_file_should_be_scanned(G.INPUT_FILENAME):
                    G.INPUT_FILENAME_REL = G.INPUT_FILENAME.replace(G.INPUT_DIR + '/', '')
                    G.FILE_DICT[filenum] = G.INPUT_FILENAME_REL

                    file_obj = C.InputFile(
                        G.INPUT_FILENAME,
                        G.INPUT_FILENAME_REL,
                        filenum)
                    G.INPUT_FILES.append(file_obj)
                    filenum += 1

    if filenum == 0:
        G.LOGGER.info('Found {0} files under INPUT_DIR'.format(num_files_checked))
        print_msg("Notice: Found no files that should be scanned.")
        sys.exit(0)
    else:
        if filenum == 1:
            G.LOGGER.info('Found {0} file to process...'.format(filenum))
        else:
            G.LOGGER.info('Found {0} files to process...'.format(filenum))

        if G.VERBOSE:
            # Write the list of files to process for analysis
            lst_filename = os.path.join(G.TEMP_DIR, 'files_to_process.lst')
            with open(lst_filename, "w", encoding='utf-8') as lst_file:
                for item in G.FILE_DICT.items():
                    fprint(lst_file, item)


# ===============================================================================
def damodre_get_list_of_input_files():
    G.FILE_DICT = {}

    G.LOGGER.info('=' * 80)

    damodre_get_full_list_of_input_files()
