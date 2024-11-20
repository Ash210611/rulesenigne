# pylint: disable=C0209           # Don't require formtted strings

import os  # for chdir
import subprocess
import sys

import un_re.global_shared_variables as G


# ===============================================================================
def antlr_set_env_vars(grammar):
    if G.SYSTEM_OS == 'Windows':
        delimiter = ';'
    else:
        delimiter = ':'

    new_classpath = G.SCRIPT_DIR + '/un_re/Antlr/' + G.ANTLR_JAR_FILENAME + delimiter + \
                    G.SCRIPT_DIR + f'/un_re/Antlr/{grammar}_lib'

    prev_classpath = os.environ.get('CLASSPATH', 'Not set')
    if prev_classpath != 'Not set':
        new_classpath += f'{delimiter}{prev_classpath}'

    os.environ['CLASSPATH'] = new_classpath

    os.environ['antlr4'] = 'java -jar {0}/un_re/Antlr/{1}'.format(
        G.SCRIPT_DIR,
        G.ANTLR_JAR_FILENAME)

    log_filename = G.TEMP_DIR + '/env_vars.re.log'

    if G.SYSTEM_OS == 'Windows':
        os_command = f'SET > {log_filename}'
    else:
        os_command = f'env | sort > {log_filename}'

    sys.stdout.flush()
    subprocess.call(os_command, shell=True)
    sys.stdout.flush()

    if not os.path.exists(log_filename):
        G.LOGGER.error('Error: Failed to the find the env_vars.re.log file.')
        G.LOGGER.error(f'Tried to find: {log_filename}')
        G.LOGGER.error(f'Had tried to run this command: {os_command}')
