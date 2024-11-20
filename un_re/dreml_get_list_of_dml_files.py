# pylint: disable=C0209           		# Don't require formtted strings
# pylint: disable=R0911				# Too many return statements

import os
import re
import sys

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.dreml_list_files_by_sha import dreml_list_files_by_sha
from un_re.find_file import find_all_files
from un_re.fprint import fprint
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.indent_info import indent_info
from un_re.print_msg import print_and_log_msg
from un_re.should_skip_this_file import should_skip_this_file
from un_re.un_re_get_list_of_excepted_files import un_re_get_list_of_excepted_files


# ===============================================================================
def file_is_a_fitnesse_test_file(file_contents):
    return re.search('Fitnesse', file_contents, re.IGNORECASE)


# ===============================================================================
def file_is_a_lettuce_test_file(file_contents):
    return re.search('Feature:', file_contents) and \
        re.search('Scenario:', file_contents)


# ===============================================================================
def add_unique_sha(candidate_sha):
    found = False
    for sha in G.SHA_LIST:
        if sha == candidate_sha:
            found = True

    if not found:
        # G.LOGGER.debug ('Will add {0}'.format (candidate_sha))
        G.SHA_LIST.append(candidate_sha)


# ===============================================================================
def add_unique_filename_from_diff_tree(full_filename, rel_filename):
    '''
    Only add the filename if it is unique
    '''

    for _, filename in G.FILE_DICT.items():
        if rel_filename == filename:
            G.LOGGER.info(f'Apparently this file is duplicated: {rel_filename}')
            return

    filenum = len(G.INPUT_FILES)

    G.FILE_DICT[filenum] = rel_filename

    file_obj = C.InputFile(
        full_filename,
        rel_filename,
        len(G.INPUT_FILES))

    G.INPUT_FILES.append(file_obj)

    G.LOGGER.info(f'Added {filenum + 1}, {rel_filename}')


# ===============================================================================
def py_file_should_be_scanned(full_filename):
    """
    Py files have multiple criteria to check, so py files are checked
    in this function to help keep the calling function shorter.

    We can scan Python files, except the ones that reference lettuce, or
    fastload.
    """

    if os.path.basename(full_filename) == '__init__.py':
        return False
    # That just tells Python where to find library functions.

    file_contents = get_file_contents(full_filename)

    if re.search('lettuce', file_contents):
        location = full_filename.replace(G.WORKSPACE, '$WORKSPACE')
        G.LOGGER.info('Found file   : {0}'.format(location))
        indent('Skipping this file, as it appears to be a Lettuce test file.')
        return False

    if re.search('fastload', file_contents):
        location = full_filename.replace(G.WORKSPACE, '$WORKSPACE')
        G.LOGGER.info('Found file   : {0}'.format(location))
        indent('Skipping this file, as it appears to be setting up a Fast Load process.')
        return False

    return True


# ===============================================================================
def sql_file_should_be_scanned(full_filename):
    """
    Sql files have multiple criteria to check, so sql files are checked
    in this function to help keep the calling function shorter.

    We can scan SQL files, but skip the ones on a database path
    because those will be scanned by the DDL scanner, and not part of a
    DML deployment exactly.
    """

    if re.search('database', full_filename, re.IGNORECASE):
        return False

    return True


# ===============================================================================
def txt_file_should_be_scanned(full_filename):
    file_contents = get_file_contents(full_filename)

    if file_is_a_fitnesse_test_file(file_contents):
        location = full_filename.replace(G.WORKSPACE, '$WORKSPACE')

        G.LOGGER.info('Found file   : {0}'.format(location))
        indent('Skipping this file, as it appears to be a Fitnesse test file.')
        return False

    return True


# ===============================================================================
def dreml_file_should_be_scanned(full_filename):
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

    if re.search(r'.py$', full_filename, re.IGNORECASE) or \
            re.search(r'.sql$', full_filename, re.IGNORECASE):
        return sql_file_should_be_scanned(full_filename)

    if re.search(r'.ksh$', full_filename, re.IGNORECASE) or \
            re.search(r'.BTEQ$', full_filename, re.IGNORECASE):
        return True

    if re.search(r'.txt$', full_filename, re.IGNORECASE):
        return txt_file_should_be_scanned(full_filename)

    # else:	# Skip all other file types
    return False


# ===============================================================================
def add_file_from_diff_tree(rel_filename):
    """
    Typically the first line in the diff-tree report looks like this:
    36c678f512fc23a670b62626305668fabac76c8a

    Obviously that is not a real filename, so let's check that each file
    exists, especially since a filename may have been dropped by a different
    sha.
    """

    full_filename = os.path.join(G.INPUT_DIR, rel_filename)
    found = os.path.exists(full_filename)
    if not found:
        return

    if not dreml_file_should_be_scanned(full_filename):
        return

    add_unique_filename_from_diff_tree(full_filename, rel_filename)


# ===============================================================================
def read_versions_file(version_filename):
    '''
    A valid line in the versions file will look like this:
        path1_WI00202666_RXI_ESI2_REF_1030=path1_WI00202666_RXI_ESI2_REF_1030.3415.d8b9aaab

    Notice it has 1 equals sign, and 2 dots after the equal signs.

    If the versions file is contaminated with merge-conflict markers, it
    will have other lines like these:
        <<<<<<< HEAD
        =======
        >>>>>>> path1_WI00203010_CCW_ESI2_REF_1022

    Lines without the expected delimiters are either skipped or flagged
    as invalid.
    '''

    with open(version_filename, "r", encoding='utf-8') as ver_file:
        for line in ver_file.readlines():
            line = line.rstrip()

            if line.count('=') == 0:
                continue
            if line.count('=') > 1 or line.count('.') < 2:
                print_and_log_msg("ERROR-g000  : Invalid line {0}".format(line))
                indent_info('Version filename: {0}'.format(version_filename))
                continue

            print('line = {0}'.format(line))
            sha = line.split('=')[1]
            sha = sha.split('.')[-1]
            if len(sha) > 0:
                add_unique_sha(sha)


# ===============================================================================
def dreml_get_partial_list_of_dml_files():
    for version_filename in ('feature.versions', 'protected.versions'):

        num_version_files_found = 0
        for ver_file_path in find_all_files(version_filename, G.WORKSPACE):

            if ver_file_path.find('do_not_use') > -1:
                pass  # Skip any files on this path

            elif ver_file_path.find('site-packages') > -1:
                pass  # Skip any files on this path

            else:
                # If the path says do not use, then don't!
                read_versions_file(ver_file_path)
                num_version_files_found += 1

        if G.VERBOSE:
            G.LOGGER.debug('Num {0} version files found: {1}'.format(
                version_filename,
                num_version_files_found))

    if G.VERBOSE:
        G.LOGGER.debug('Num unique shas found: {0}'.format(len(G.SHA_LIST)))

    for sha in G.SHA_LIST:

        (ret, log_filename) = dreml_list_files_by_sha(sha, G.INPUT_DIR)
        if ret == 0:
            with open(log_filename, 'r', encoding='utf-8') as log_file:
                for line in log_file.readlines():
                    rel_filename = line.rstrip()
                    add_file_from_diff_tree(rel_filename)
        else:
            G.LOGGER.error('Failed to list files by sha: {0}'.format(sha))
            sys.exit(ret)

    if len(G.FILE_DICT) == 0:
        print_and_log_msg((' ' * 15) + 'WARNING: Failed to find any files to scan!')


# ===============================================================================
def dreml_get_full_list_of_dml_files():
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
                if dreml_file_should_be_scanned(G.INPUT_FILENAME):
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
        print_and_log_msg("Notice: Found no files that should be scanned.")
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
def dreml_get_list_of_dml_files():
    G.FILE_DICT = {}

    G.LOGGER.info('=' * 80)

    un_re_get_list_of_excepted_files()

    if G.DIR_SCAN_TYPE == 'FULL':
        dreml_get_full_list_of_dml_files()

    elif G.DIR_SCAN_TYPE == 'RECENT':
        dreml_get_partial_list_of_dml_files()
