# pylint: disable=C0209           		# Don't require formtted strings
# pylint: disable=R0911				# Too many return statements

import os
import re
import sys

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.fprint import fprint
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.should_skip_this_file import should_skip_this_file
from un_re.un_re_get_list_of_excepted_files import un_re_get_list_of_excepted_files


# ===============================================================================
def py_file_should_be_scanned(full_filename):
    if os.path.basename(full_filename) == '__init__.py':
        return False
    # That just tells Python where to find library functions.

    file_contents = get_file_contents(full_filename)

    if not re.search(r'spark\.sql\s?\(', file_contents, re.MULTILINE):
        location = full_filename.replace(G.WORKSPACE, '$WORKSPACE')
        G.LOGGER.info('Found file   : {0}'.format(location))
        indent('Skipping this file, as it does not call spark.sql().')
        return False

    return True


# ===============================================================================
def databricks_file_should_be_scanned(full_filename):
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

    if G.INPUT_FILENAME.find('site-packages') > -1:
        return False  # Skip files on this path.

    if should_skip_this_file(full_filename):
        # Skip it if this filename is on the exception list of files
        # to be skipped
        return False

    if re.search(r'.py$', full_filename, re.IGNORECASE) or \
            re.search(r'.sql$', full_filename, re.IGNORECASE):
        return True

    # else:	# Skip all other file types
    return False


# ===============================================================================
def databricks_get_full_list_of_input_files():
    filenum = 0
    # for subdir, dirs, files in os.walk(G.INPUT_DIR):
    for subdir, _, files in os.walk(G.INPUT_DIR):
        for this_file in sorted(files):
            G.INPUT_FILENAME = subdir + os.sep + this_file

            if databricks_file_should_be_scanned(G.INPUT_FILENAME):
                G.INPUT_FILENAME_REL = G.INPUT_FILENAME.replace(G.INPUT_DIR + '/', '')
                G.FILE_DICT[filenum] = G.INPUT_FILENAME_REL

                file_obj = C.InputFile(
                    G.INPUT_FILENAME,
                    G.INPUT_FILENAME_REL,
                    filenum)
                G.INPUT_FILES.append(file_obj)
                filenum += 1

    if filenum == 0:
        G.LOGGER.info('Found 0 files under INPUT_DIR that should be scanned')
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
def databricks_get_list_of_input_files():
    G.FILE_DICT = {}

    G.LOGGER.info('=' * 80)

    un_re_get_list_of_excepted_files()

    databricks_get_full_list_of_input_files()

# for TERADATA_DML, we would ahve the option at this point to get the
# recent files, and so far for Databricks, we are only getting the full
# list.

# PLUS, for TERADATA_DDL, the CCW-D pipeline populates a
# feature.versions file with the SHAs from the last 2 commits, so we
# can tell what commits to scan.   The DATABRICKS pipeline has not
# been developed, so it is unknown if that is available.
