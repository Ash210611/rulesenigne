# pylint: disable=C0209			# Don't require formatted strings.
# pylint: disable=W1202			# Don't require logger formatting

# File: process_one_file.py
#
# That function is called by process_files.py
#
# The main function in this module is process_one_file ().
#
# ===============================================================================
import glob  # for glob.glob, finding filenames with a wildcard
import os
import re
import shutil
import sys

import time

import un_re.global_shared_variables as G

from un_re.add_thread_log_to_main_log import add_thread_log_to_main_log
from un_re.antlr_parse_stmt import antlr_parse_stmt
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.indent_error import indent_error
from un_re.make_local_script_dir import make_local_script_dir
from un_re.print_msg import print_msg
from un_re.process_one_sql_stmt import process_one_sql_stmt
from un_re.setup_logging import setup_logging
from un_re.setup_logging import setup_thread_logging
from un_re.setup_logging import set_verbose_logging
from un_re.setup_logging import closeup_thread_logging


# ===============================================================================
def process_one_sql_file_setup():
    G.INPUT_FILENAME_REL = G.FILE_DICT[G.FILE_NUM]

    if G.RULES_ENGINE_TYPE == 'TERADATA_DDL':
        G.INPUT_FILENAME = G.XML_DIR + '/' + G.FILE_DICT[G.FILE_NUM]
    else:
        G.INPUT_FILENAME = G.INPUT_DIR + '/' + G.FILE_DICT[G.FILE_NUM]

    if not os.path.isfile(G.INPUT_FILENAME):
        print_msg("ERROR.         This filename is not found.")
        indent_error(f'Tried to find: {G.INPUT_FILENAME}')
        indent_error('RULES_ENGINE_TYPE : {0}'.format(G.RULES_ENGINE_TYPE))
        indent_error('INPUT_DIR         : {0}'.format(G.INPUT_DIR))
        indent_error('INPUT_FILENAME_REL: {0}'.format(G.INPUT_FILENAME_REL))
        indent_error('')
        sys.exit(37)

    G.THREAD_LOG_FILENAME = G.TEMP_DIR + "/" + \
                            os.path.basename(G.INPUT_FILENAME) + '.' + \
                            str(G.FILE_NUM + 1) + '.re.log'

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
    G.LOGGER.info('Location     = %s', location)

    # Reinitialize certain globals that are left over from the previous
    # INPUT_FILENAME and should be reset.

    G.DATABASE_BASE = ''
    G.DATABASE_NUM = -1


# ===============================================================================
def process_one_sql_file_closeup(num_stmts):
    G.LOGGER.info('')

    if num_stmts > 1:
        G.LOGGER.info('File {0} had {1} statements to process.'.format(
            G.FILE_NUM + 1,
            num_stmts))
    elif num_stmts == 1:
        G.LOGGER.info('File {0} had 1 statement to process.'.format(
            G.FILE_NUM + 1))
    else:
        G.LOGGER.info('File {0} had 0 statements to process.'.format(
            G.FILE_NUM + 1))

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
def process_one_file_sql_statements():
    G.LOGGER.info('')
    indent('=' * 72)

    wildcard_spec = G.TEMP_DIR + '/' + G.INPUT_FILENAME_REL + '.*.sql'
    sql_filenames = sorted(glob.glob(wildcard_spec))

    if len(sql_filenames) == 0:
        indent('No filenames were found to scan.')
        return 0

    indent('The following statements were parsed:')

    skip_the_rest = False
    sql_stmt_obj = None  # For Pycharm linting
    for sql_filename in sql_filenames:

        found_sql_stmt_obj = False
        for sql_stmt_obj in G.SQL_STATEMENT_OBJS:
            if sql_stmt_obj.local_script_name == sql_filename:
                found_sql_stmt_obj = True
                break

        if not found_sql_stmt_obj:
            print('Uh-Oh, did not find sql_stmt_obj for this local_script_name:')
            print(f'       {sql_filename}')

        if skip_the_rest:
            # Create a placeholder file to keep the list of sql
            # statements in sync with the number of Antlr logs
            skip_filename = sql_filename + '.skipped.antlr.re.log'
            shutil.copyfile(sql_filename, skip_filename)
            if sql_stmt_obj is not None:
                sql_stmt_obj.antlr_status = 'SKIPPED'
            continue

        # Parse each SQL statement with Antlr.
        sql_stmt_obj.sql_stmt_txt = get_file_contents(sql_filename)
        ret = process_one_sql_stmt(sql_stmt_obj)
        if ret != 0:
            # process no more SQL statements for this file
            skip_the_rest = True
            total_num_stmts = len(sql_filenames)
            num_stmts_to_skip = total_num_stmts - sql_stmt_obj.sql_stmt_num - 1
            if num_stmts_to_skip == 0:
                G.LOGGER.info('Notice-g003  : Subsequent statements would be skipped, but there are no more.')

            elif num_stmts_to_skip == 1:
                print_msg('Notice-g003  : {0} subsequent statement will be left unchecked.'.format(
                    num_stmts_to_skip))
            elif num_stmts_to_skip > 1:
                print_msg('Notice-g003  : {0} subsequent statements will be left unchecked.'.format(
                    num_stmts_to_skip))

            # It is appropriate to skip the remaining SQL statements
            # in this file.  But this function is running in
            # parallel, so we need a way to persist that finding
            # so we can also skip trying to get the antlr findings
            # from sql_statements that were skipped.
            #
            # If it had succeeded, the Antlr log filename would
            # be named sql_filename+'.antlr.re.log'
            #
            # If failure occurs, the logfile will be named
            # sql_filename+'.failed.antlr.re.log'
            #
            # That filename will signal the get_all_antlr_findings
            # function to skip the remaining antlr logs
            # after a failure occurred.

            continue

    return sql_stmt_obj.sql_stmt_num + 1


# ===============================================================================
def process_one_esp_file():
    _, file_extension = os.path.splitext(G.INPUT_FILENAME)

    if not re.search(r'\.wld', file_extension, re.IGNORECASE):
        G.LOGGER.info('Skipping this file - Unknown extension.')
        return []

    # Make a local copy of the ESP file for Antlr to analyze.
    G.LOCAL_SCRIPT_NAME = G.TEMP_DIR + '/' + G.INPUT_FILENAME_REL

    G.LOCAL_SCRIPT_NAME = G.LOCAL_SCRIPT_NAME.replace(' ', '_')

    local_script_dir = os.path.dirname(G.LOCAL_SCRIPT_NAME)

    make_local_script_dir(local_script_dir)

    shutil.copy(G.INPUT_FILENAME, G.LOCAL_SCRIPT_NAME)

    # print ('INPUT_FILENAME	  = {0}'.format (G.INPUT_FILENAME))
    # print ('INPUT_FILENAME_REL      = {0}'.format (G.INPUT_FILENAME_REL))
    # print ('LOCAL_SCRIPT_NAME       = {0}'.format (G.LOCAL_SCRIPT_NAME))

    antlr_parse_stmt('ESP', G.LOCAL_SCRIPT_NAME)

    return 1


# ===============================================================================
# This function will process one input DDL file.
# In the Parallel version of this, at the moment this function is called,
# the memory for this process has been cloned to a new child.
# That has implications for how the global variables are understood.
# The global variables are only global to the child process now.

def process_one_sql_file(file_num):
    G.FILE_NUM = file_num

    process_one_sql_file_setup()

    num_statements_found = process_one_file_sql_statements()

    process_one_sql_file_closeup(num_statements_found)

    return num_statements_found
