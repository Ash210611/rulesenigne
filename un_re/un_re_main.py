# pylint: disable=C0209			# Don't require formatted strings.
# pylint: disable=W1202			# Don't require lazy logger formatting

import getopt
import os
# ======== ========= ========= ========= ========= ========= ========= ==========
import sys
import time
from datetime import datetime
from time import gmtime, strftime

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G
from un_re.antlr_compile_grammar import antlr_compile_grammar
from un_re.cleanup_old_tmp_directories import cleanup_old_tmp_directories
from un_re.count_stmts_processed import count_stmts_processed
from un_re.display_summary_message import display_summary_message
from un_re.display_validated_input_args import display_validated_input_args
from un_re.get_memory_used import get_memory_used
from un_re.initialize_env_variables import initialize_env_variables
from un_re.load_erwin_json_to_dkc import load_erwin_json_to_dkc
from un_re.post_success_event_records import post_success_event_records
from un_re.print_msg import print_msg
from un_re.print_startup_messages import print_startup_messages
from un_re.process_files import process_files
from un_re.read_the_list_of_input_files import read_the_list_of_input_files
from un_re.setup_logging import set_verbose_logging
from un_re.setup_main_environment import setup_main_environment
from un_re.validate_input_arguments import validate_input_arguments
from un_re.write_junit_xml import write_junit_xml

# ======== ========= ========= ========= ========= ========= ========= ==========
sys.dont_write_bytecode = True

T1 = datetime.now()


# ======== ========= ========= ========= ========= ========= ========= ==========
# Give the user a usage explanation if they ask for one.

def show_usage():
    """

This is the Database Rules Engine script.    This script will support the 
database part of the OneApp process.

Usage:
        python3.9 UN_RE.py -i INI_FILE [OPTIONS]

where
        -i INI_FILE contains the input variables that control operation of this
                script.  The INI file should have a Windows INI file format, 
                with a section at the top identifying it as [UN_RE].

        -d do NOT decomment the Liquibase.XML file before reading the
                        include file specifications from it.  Otherwise, 
                        include files will be read from anywhere in the file, 
                        including comments.

		-v is the verbose option, which prints more output messages.

The available INI variables are:
        RULES_ENGINE_TYPE specifies the SQL language to parse the input SQL as.
                Currently, it also designates a list of rules that will be
                checked for that language.

		XML_FILENAME=[path] supplies the full, absolute path to the Liquibase
                XML file, including the filename.   
                If RULES_ENGINE_TYPE=ORE, this filename is expected to be
                named "master.xml".
		Otherwises it is expected to be named 'liquibase.xml'.

        INPUT_DIR specifies the DIRECTORY where source files will be found.
                That directory will be searched with the "find" command, so
                files can be saved in any subdirectory.

        PARALLEL_DEGREE=# specifies the number of files to parse in parallel,
                which can save a little time on large deployments.

        VERBOSE=[TRUE|FALSE], is an alternative to the -v switch.

        ========================================================================

Each rule checked by that Rules Engine can be switched on or off independently
        and individually.

Change the resources/rules.lst file to enable to disable specific rules.

EOF

	"""
    print(show_usage.__doc__)
    sys.exit(2)


# ======== ========= ========= ========= ========= ========= ========= ==========
def read_command_line_arguments(argv):
    argv_opts = argv[1:]
    selected_opts = []

    try:
        selected_opts, _ = getopt.getopt(argv_opts, "adhi:v", ["ifile=", "ofile="])
    except getopt.GetoptError:
        show_usage()

    for opt, arg in selected_opts:
        if opt == '-d':
            G.DECOMMENT_XML = False
        elif opt == '-h':
            show_usage()
        elif opt in ("-i", "--ifile"):
            G.INI_FILENAME = arg
        elif opt == '-v':
            G.VERBOSE = True
            set_verbose_logging()
        else:
            print('Illegal option. Use -h for help.')
            sys.exit(5)


# ======== ========= ========= ========= ========= ========= ========= ==========
def closeup_main_environment():
    # global	T1	# Is assigned above

    cleanup_old_tmp_directories()

    write_junit_xml()

    ret = display_summary_message()

    if G.LOAD_EVENT_RECORDS:
        # Post the success records for files that had no findings.
        total_num_json_records = post_success_event_records()

        G.LOGGER.info(
            'Will need to load {0} event records into the historical repository.'.format(total_num_json_records))

    if G.RULES_ENGINE_TYPE == 'DATA_MODEL':
        load_erwin_json_to_dkc()

    G.LOGGER.info('')
    G.LOGGER.info(G.SCRIPT_NAME + ' started at ' + G.START_TIME)
    G.LOGGER.info(G.SCRIPT_NAME + ' is done at ' + strftime('%Y-%m-%d_%H.%M.%S', gmtime()))
    G.LOGGER.info('               Done with all cleanup functions.')
    G.LOGGER.info('TEMP_DIR     = {0}'.format(G.TEMP_DIR))
    G.LOGGER.info('INPUT_DIR    = {0}'.format(G.INPUT_DIR))

    G.LOGGER.info('=' * 88)

    G.LOGGER.info('Num Files Processed = {0}'.format(len(G.FILE_DICT)))

    if G.RULES_ENGINE_TYPE in ('DB2_RE', 'SNOWFLAKE', 'DATABRICKS', 'ORE'):
        G.LOGGER.info('Num Stmts Processed = {0}'.format(len(G.SQL_STATEMENT_OBJS)))
    # SQL statements for these types don't have to be terminated with a semi-colon.
    # So if Antlr cannot read them, there is not another way to
    # recognize how many statements there would have been

    else:
        if G.RULES_ENGINE_TYPE == 'ESP_RE':
            ns_processed = G.COMMAND_COUNTER['ESP STATEMENT']
            ns_total = ns_processed

        else:
            (ns_processed, ns_total) = count_stmts_processed()

        G.LOGGER.info('Num Stmts Processed = {0} of {1}'.format(ns_processed, ns_total))

        if G.RULES_ENGINE_TYPE != 'ESP_RE':
            if ns_processed < ns_total:
                G.LOGGER.info('(Stmts are skipped when syntax cannot be read.)')

    t2 = datetime.now()
    elapsed_time = t2 - T1
    G.LOGGER.info('Techdebt used: {0} times'.format(G.TECHDEBT_USAGE_COUNT))
    G.LOGGER.info('Memory   used: {0:.1f} Mb'.format(get_memory_used()))
    G.LOGGER.info('Time     used: {0:d} seconds'.format(1 + int(elapsed_time.total_seconds())))

    time.sleep(1)  # Sleep for a second so any jobs after that will
    # give their temporary directory a different
    # name.

    G.LOGGER.info('Done.')
    # Return 66 to indicate errors were found.
    # Return 67 to indicate warnings were found.

    return ret


# ======== ========= ========= ========= ========= ========= ========= ==========
def compile_specified_Antlr_grammar():
    '''
	Compile the Antlr grammar once before possibly calling it in parallel.

	If you need additional diagnostics, you could call the compiler like this:
		ret, antlr_log_filename = antlr_compile_grammar ('TD16')
	'''

    if G.RULES_ENGINE_TYPE in ('TERADATA_DDL', 'TERADATA_DML', 'DATAOPS_TDV_DDL', 'DAMODRE'):

        antlr_compile_grammar('TD16')
        antlr_compile_grammar('TD15_comment_on')

    elif G.RULES_ENGINE_TYPE == 'HIVE_DDL_RE':
        antlr_compile_grammar('Hplsql')

    elif G.RULES_ENGINE_TYPE == 'PG_RE':
        antlr_compile_grammar('PG')

    elif G.RULES_ENGINE_TYPE == 'DB2_RE':
        antlr_compile_grammar('DB2_115')

    elif G.RULES_ENGINE_TYPE == 'SNOWFLAKE':
        antlr_compile_grammar('SNOWFLAKE')

    elif G.RULES_ENGINE_TYPE == 'DATABRICKS':
        antlr_compile_grammar('DATABRICKS')

    elif G.RULES_ENGINE_TYPE == 'ORE':
        antlr_compile_grammar('ORA23')

    elif G.RULES_ENGINE_TYPE == 'REDSHIFT':
        antlr_compile_grammar('REDSHIFT')

    elif G.RULES_ENGINE_TYPE == 'DATA_MODEL':
        pass

    elif G.RULES_ENGINE_TYPE == 'ESP_RE':
        antlr_compile_grammar('ESP')

    else:
        print_msg('{0}: Unknown RULES_ENGINE_TYPE: {1}'.format(os.path.basename(__file__), G.RULES_ENGINE_TYPE))
        sys.exit(E.UNKNOWN_RULES_ENGINE_TYPE)


# ======== ========= ========= ========= ========= ========= ========= ==========
def main():
    setup_main_environment()

    read_command_line_arguments(sys.argv)  # See function above for that.

    print_startup_messages('Running the DA DevOps Unified Rules Engine.')

    initialize_env_variables()

    validate_input_arguments()  # See function above for that.

    display_validated_input_args()

    compile_specified_Antlr_grammar()

    read_the_list_of_input_files()

    # Finally, process the list of files for real.
    process_files()

    ret = closeup_main_environment()

    G.LOGGER.info('Returning exit code {0}'.format(ret))

    print(ret)
