# pylint:	disable=C0209			# Don't require formatted strings

import glob
import re

import un_re.global_shared_variables as G
from un_re.check_g012 import check_g012
from un_re.check_r416 import check_r416
from un_re.get_file_contents import get_file_contents
from un_re.get_hive_antlr_findings import get_hive_antlr_findings
from un_re.notice_file_findings import notice_file_findings
from un_re.print_command_summary import print_command_summary
from un_re.print_msg import print_msg
from un_re.rezero_the_command_counters import rezero_the_command_counters


# ===============================================================================
def get_hive_antlr_findings_from_1_file(file_num):
    # Use this for SQL files, not ESP files.

    G.FILE_OBJ = G.INPUT_FILES[file_num]
    wildcard_spec = G.TEMP_DIR + '/' + G.INPUT_FILENAME_REL + '.*.antlr.re.log'

    antlr_log_filenames = sorted(glob.glob(wildcard_spec))

    num_antlr_log_filenames = len(antlr_log_filenames)
    found_a_failure = False

    for i in range(num_antlr_log_filenames):
        G.ANTLR_LOG_FILENAME = antlr_log_filenames[i]

        if G.VERBOSE:
            G.LOGGER.debug('')
            G.LOGGER.debug('Filename     : {0}'.format(G.ANTLR_LOG_FILENAME.replace(
                G.TEMP_DIR + '/', '$TEMP_DIR' + '/')))

        if found_a_failure:
            if G.VERBOSE:
                G.LOGGER.debug('Antlr status : Skipped.')
                continue

        elif re.search(r'failed.antlr.re.log', G.ANTLR_LOG_FILENAME):
            found_a_failure = True
            if G.VERBOSE:
                G.LOGGER.debug('Antlr status : Failed with a syntax error.')

                G.FILE_OBJ.has_a_syntax_error = True
                # Must set that flag again, because it is not
                # saved during the antlr_parse_stmt phase that
                # runs in parallel child processes
                continue

        G.ANTLR_LOG_CONTENTS = get_file_contents(G.ANTLR_LOG_FILENAME)

        if re.search(r'Antlr syntax check succeeded.', G.ANTLR_LOG_CONTENTS):
            get_hive_antlr_findings(G.ANTLR_LOG_FILENAME)

        else:
            G.RULE_ID = 'g003'

            this_filename = G.ANTLR_LOG_FILENAME.replace(G.TEMP_DIR + '/', '')
            this_filename = this_filename.replace('.sql.skipped.antlr.re.log', '')

            print_msg('Notice-{0}  : Failed to check {1}.'.format(
                G.RULE_ID,
                this_filename))
            notice_file_findings(G.INPUT_FILENAME)

            G.INPUT_FILES[file_num].has_a_syntax_error = True


# ===============================================================================
def get_all_hive_antlr_findings():
    '''
    Now that the input files have been parsed, load their findings
    from the Antlr log files into the class objects

    This function will loop through all input filenames, and statements
    from each file, and call the get_antlr_findings function for each one.
    '''

    G.LOGGER.info('Reading results from the Antlr syntax-parsing step...')

    for G.FILE_NUM in range(len(G.FILE_DICT)):
        G.LOGGER.info('=' * 88)
        G.LOGGER.info('File Number  = {0}.'.format(
            G.FILE_NUM + 1))

        if not G.INPUT_FILES[G.FILE_NUM].is_utf8_readable:
            continue

        rezero_the_command_counters()

        G.INPUT_FILENAME_REL = G.FILE_DICT[G.FILE_NUM]

        G.INPUT_FILENAME = G.INPUT_DIR + '/' + G.FILE_DICT[G.FILE_NUM]

        # Check rules that apply to the whole filename here
        if 'r416' in G.SHOULD_CHECK_RULE:
            check_r416(G.INPUT_FILENAME)  # no control characters
        if 'g012' in G.SHOULD_CHECK_RULE:
            check_g012(G.INPUT_FILENAME)  # valid ruleset indicator

        get_hive_antlr_findings_from_1_file(G.FILE_NUM)

        print_command_summary()

    G.LOGGER.info('Done reading results from the Antlr syntax-parsing step.')
    return 0
