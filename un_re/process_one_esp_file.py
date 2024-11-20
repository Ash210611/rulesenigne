# pylint: disable=W1203			# Don't require formatted strings.
# pylint: disable=W1202			# Don't require lazy logger formatting
# pylint: disable=C0209			# Don't require formatted strings.

# File: process_one_file.py
#
# That function is called by process_files.py
#
# The main function in this module is process_one_file ().
#
# ===============================================================================
import os
import re
import shutil
import sys

import time

import un_re.global_shared_variables as G

from un_re.add_thread_log_to_main_log import add_thread_log_to_main_log
from un_re.antlr_parse_stmt import antlr_parse_stmt
from un_re.make_local_script_dir import make_local_script_dir
from un_re.print_msg import print_msg
from un_re.setup_logging import setup_logging
from un_re.setup_logging import setup_thread_logging
from un_re.setup_logging import set_verbose_logging
from un_re.setup_logging import closeup_thread_logging


# ===============================================================================
def process_one_esp_file_setup():
    G.INPUT_FILENAME_REL = G.FILE_DICT[G.FILE_NUM]

    G.INPUT_FILENAME = G.INPUT_DIR + '/' + G.FILE_DICT[G.FILE_NUM]

    if not os.path.isfile(G.INPUT_FILENAME):
        print_msg("ERROR.         This filename is not found.")
        G.LOGGER.error(f'Tried to find: {G.INPUT_FILENAME}')
        G.LOGGER.error(f'Input_filename_rel: {G.INPUT_FILENAME_REL}')
        G.LOGGER.error('')
        sys.exit(37)

    G.THREAD_LOG_FILENAME = G.TEMP_DIR + "/" + \
                            os.path.basename(G.INPUT_FILENAME) + '.' + \
                            str(G.FILE_NUM + 1) + 're.log'

    if G.PARALLEL_DEGREE > 1:
        setup_thread_logging(G.THREAD_LOG_FILENAME, G.FILE_NUM)
        if G.VERBOSE:
            set_verbose_logging()

        sys.stdout.flush()

    G.LOGGER.info('=' * 88)
    G.LOGGER.info('File Number  = {0}, started at {1}.'.format(
        G.FILE_NUM + 1,
        time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime())))
    location = G.INPUT_FILENAME.replace(G.WORKSPACE, '$WORKSPACE')
    G.LOGGER.info(f'Location     = {location}')


# ===============================================================================
def process_one_esp_file_closeup():
    G.LOGGER.info('File {0}, {1}, is done at {2}.'.format(
        G.FILE_NUM + 1,
        G.INPUT_FILENAME.replace(G.WORKSPACE, '$WORKSPACE'),
        time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime())))

    if G.PARALLEL_DEGREE > 1:
        # As the last steps in this function, display any messages reported
        # by this function back to the parent process

        closeup_thread_logging(G.THREAD_LOG_FILENAME)
        setup_logging(G.LOG_FILENAME)
        if G.VERBOSE:
            set_verbose_logging()

        add_thread_log_to_main_log()

    sys.stdout.flush()


# ===============================================================================
def process_one_esp_file(file_num):
    '''
    This function will process one input ESP file.
    '''

    G.FILE_NUM = file_num

    process_one_esp_file_setup()

    _, file_extension = os.path.splitext(G.INPUT_FILENAME)

    if not re.search('\.wld', file_extension, re.IGNORECASE):
        G.LOGGER.info('Skipping this file - Unknown extension.')
        return []

    # Make a local copy of the ESP file for Antlr to analyze.
    G.LOCAL_SCRIPT_NAME = G.TEMP_DIR + '/' + G.INPUT_FILENAME_REL

    G.LOCAL_SCRIPT_NAME = G.LOCAL_SCRIPT_NAME.replace(' ', '_')

    local_script_dir = os.path.dirname(G.LOCAL_SCRIPT_NAME)

    make_local_script_dir(local_script_dir)

    shutil.copy(G.INPUT_FILENAME, G.LOCAL_SCRIPT_NAME)

    antlr_parse_stmt('ESP', G.LOCAL_SCRIPT_NAME)

    num_statements_found = 1

    process_one_esp_file_closeup()

    return num_statements_found
