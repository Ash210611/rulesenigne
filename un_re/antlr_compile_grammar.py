# pylint: disable=C0209           # Don't require formtted strings

import os  # for path.exists
import re
import subprocess
import sys  # for exit
import time  # for time and nanoseconds

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G
from un_re.antlr_create_lib_dir import antlr_create_lib_dir
from un_re.antlr_create_logs_dir import antlr_create_logs_dir
from un_re.antlr_get_jar_file import antlr_get_jar_file
from un_re.antlr_set_env_vars import antlr_set_env_vars
from un_re.get_file_contents import get_file_contents
from un_re.indent_info import indent_info
from un_re.indent_warning import indent_warning


# ===============================================================================
def should_compile(grammar_file: str, parser_file: str) -> bool:
    '''
	Compiling the grammar file produces a parser file.

	Compare the last-modification time of the grammar file to the parser file.

	For example
	grammar_mtime 	= 1588890623.061659
	parser_mtime	= 1588890587.8282151

	Since the grammar_mtime > parser_mtime, it is later, which is newer,
	so the grammar file should be recompiled to produce a new, updated
	parser file.
	'''

    if not os.path.exists(parser_file):
        return True

    grammar_mtime = os.path.getmtime(grammar_file)
    parser_mtime = os.path.getmtime(parser_file)

    if grammar_mtime > parser_mtime:
        return True

    return False


# ===============================================================================
def antlr_call_javac(grammar: str) -> None:
    os.chdir(G.SCRIPT_DIR + f'/un_re/Antlr/{grammar}_lib')

    os_command = 'javac -g:none *.java'
    # -----------------------------------------------------------------------
    try:
        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error(f'Child was terminated by signal {-ret}')
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

    except OSError as e:
        G.LOGGER.error(f'Antlr execution failed: {e}')
        sys.exit(E.ANTLR_EXECUTION_FAILED)


# ===============================================================================
def antlr_compile_grammar_report_issue(log_line, logfile_contents, nanoseconds):
    indent_warning('Grammatical error')
    indent_warning(log_line)
    indent_warning('')

    print('-' * 50)
    print('Logfile contents:')
    print(logfile_contents)
    print('-' * 50)
    sys.stdout.flush()

    javac_filename = G.TEMP_DIR + '/compile.{0}.antlr.javac.log'.format(nanoseconds)
    os_command = f'javac -version > {javac_filename} 2>&1'
    ret = subprocess.call(os_command, shell=True)
    javacfile_contents = get_file_contents(javac_filename)
    print('-' * 50)
    print(f'Return code = {ret}')
    print('javac -version:')
    print(javacfile_contents)
    print('-' * 50)
    sys.stdout.flush()

    env_filename = G.TEMP_DIR + '/compile.{0}.antlr.env.log'.format(nanoseconds)
    os_command = f'env | sort > {env_filename} 2>&1'
    ret = subprocess.call(os_command, shell=True)
    envfile_contents = get_file_contents(env_filename)
    print('-' * 50)
    print(f'Return code = {ret}')
    print('env | sort:')
    print(envfile_contents)
    print('-' * 50)

    sys.exit(E.ANTLR_EXECUTION_FAILED)


# ===============================================================================
def antlr_compile_grammar(grammar: str):
    '''
	This script will compile the designated grammar file, but it will not 
	parse the file DDLs.  To do that, use the nearby antlr_parse_stmt 
	function

	When testing from a shell script, it can be handy to define grun as:
		grun = 'java org.antlr.v4.gui.TestRig'
	'''

    antlr_get_jar_file()
    antlr_create_lib_dir(grammar)
    antlr_create_logs_dir(grammar)

    antlr_set_env_vars(grammar)  # We probably only need to call this
    # from the antlr_compile_grammar function

    nanoseconds = f'{time.time():.9f}'
    log_filename = G.TEMP_DIR + '/compile.{0}.antlr.re.log'.format(nanoseconds)

    grammar_file = G.SCRIPT_DIR + '/un_re/Antlr/{0}.g4'.format(grammar)
    parser_file = G.SCRIPT_DIR + '/un_re/Antlr/{0}_lib/{0}Parser.class'.format(grammar)

    if not should_compile(grammar_file, parser_file):
        G.LOGGER.info('               Note: The grammar file for {0} is already compiled.'.format(grammar))
        return 0, log_filename

    antlr4 = 'java -jar {0}/{1}'.format(
        G.SCRIPT_DIR + '/un_re/Antlr',
        G.ANTLR_JAR_FILENAME)

    lib_dir = G.SCRIPT_DIR + '/un_re/Antlr/{0}_lib'.format(grammar)

    os_command = '{0} -o {1} -lib {1} {2} >{3} 2>&1 '.format(
        antlr4,
        lib_dir,
        grammar_file,
        log_filename)

    sys.stdout.flush()  # Always flush the console log
    # output before calling a system function.

    # -----------------------------------------------------------------------
    try:
        indent_info(f'Compiling the grammar file for {grammar}...')

        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error(f'Child was terminated by signal {-ret}')
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

    except OSError as e:
        G.LOGGER.error('Antlr execution failed: {0}'.format(e))
        sys.exit(E.ANTLR_EXECUTION_FAILED)

    # -----------------------------------------------------------------------
    # If here, ret >= 0

    if not os.path.exists(log_filename):
        G.LOGGER.error('ERROR       : Antlr log file not found')
        G.LOGGER.error('Tried to find {0}'.format(log_filename))
        return E.FILE_NOT_FOUND, log_filename

    logfile_contents = get_file_contents(log_filename)

    # Check for issues
    found_an_issue = False

    log_line = ''
    for log_line in logfile_contents.split('\n'):

        if re.search('warning', log_line):
            found_an_issue = True
            break

        if re.search('syntax error', log_line):
            found_an_issue = True
            break

        if re.search(r'error\([0-9]*\)', log_line):
            found_an_issue = True
            break

        if re.search(r'Error: A JNI error has occurred', log_line):
            found_an_issue = True
            break

    if found_an_issue:
        antlr_compile_grammar_report_issue(log_line, logfile_contents, nanoseconds)

    antlr_call_javac(grammar)

    if G.VERBOSE:
        G.LOGGER.debug('Good         : Antlr grammar successfully compiled.')

    sys.stdout.flush()  # Always flush the console log-file

    return ret, log_filename
