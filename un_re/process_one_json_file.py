# pylint: disable=C0209			# Don't require formatted strings

# File: process_one_json_file.py
#
# That function is called by process_files.py
#
# The main function in this module is process_one_json_file ().
#
# ===============================================================================
import os
import sys

import time

import un_re.global_shared_variables as G

from un_re.clean_file import clean_file
from un_re.indent_info import indent_info
from un_re.load_json_globals import load_json_globals
from un_re.print_msg import print_msg

import un_re.extractModelJson as J


# ===============================================================================
def process_one_json_file_setup(file_num):
    G.FILE_NUM = file_num

    G.INPUT_FILENAME_REL = G.FILE_DICT[G.FILE_NUM]

    G.INPUT_FILENAME = G.INPUT_DIR + '/' + G.FILE_DICT[G.FILE_NUM]

    if not os.path.isfile(G.INPUT_FILES[file_num].input_filename):
        print_msg("ERROR.         This filename is not found.")
        G.LOGGER.error(f'Tried to find: {G.INPUT_FILENAME}')
        G.LOGGER.error(f'Input_filename_rel: {G.INPUT_FILENAME_REL}')
        G.LOGGER.error('')
        sys.exit(37)

    G.LOGGER.info('=' * 88)
    G.LOGGER.info('File Number  = {0}, started at {1}.'.format(
        G.FILE_NUM + 1,
        time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime())))
    location = G.INPUT_FILENAME.replace(G.WORKSPACE, '$WORKSPACE')
    G.LOGGER.info('Location     = %s' % location)

    clean_file(G.INPUT_FILES[G.FILE_NUM].input_filename)


# ===============================================================================
def process_one_json_file_closeup():
    G.LOGGER.info('')

    indent_info('File {0}, {1}, is done at {2}.'.format(
        G.FILE_NUM + 1,
        G.INPUT_FILENAME.replace(G.WORKSPACE, '$WORKSPACE'),
        time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime())))


# ===============================================================================
def process_one_json_file(file_num):
    '''
    This function will process one input JSON file.

    JSON files don't have SQL statements, rather they have records.
    '''

    if G.RULES_ENGINE_TYPE != 'DATA_MODEL':
        return 0

    process_one_json_file_setup(file_num)

    J.extractJson(
        os.path.dirname(G.INPUT_FILENAME),
        os.path.basename(G.INPUT_FILENAME))

    # --------------------------------------------------------------------------
    # At this point, all the records from the input JSON file have been inserted
    # into sqlite tables.

    load_json_globals()

    process_one_json_file_closeup()

    return 0
