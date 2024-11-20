import getpass
import os
import platform
import re
import subprocess
import sys
import time

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G

from un_re.setup_logging import setup_logging
from un_re.print_msg import print_msg


# ======== ========= ========= ========= ========= ========= ========= ==========
def validate_temp_dir_path(temp_dir):
    '''
    Doing this to satisfy Veracode.
    See: https://community.veracode.com/s/article/how-do-i-fix-cwe-73-external-control-of-file-name-or-path-in-java
    '''
    if not re.search(r'/tmp/', temp_dir) or \
            not re.search(r'[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}.[0-9]{2}.[0-9]{2}', temp_dir):
        print_msg('ERROR: Failed to validate temp_dir')
        print(f'Tried to validate: {temp_dir}')
        sys.exit(E.INVALID_INPUT)

    return temp_dir


# ======== ========= ========= ========= ========= ========= ========= ==========
def setup_main_environment():
    '''
    G.SCRIPT_DIR is the name of the directory where this file (__file__)
    is found.

    G.SCRIPT_NAME is the name of the entry point (sys.argv[0])

    G.TEMP_DIR is the name of a temporary directory in the WORKSPACE

    While it can be convenient to create the TEMP_DIR under the SCRIPT_DIR,
    it comes in handy to keep TEMP_DIR separate from the scripts for
    diagnostic purposes.
    '''

    # Get the SCRIPT_NAME from argv[0]
    this_dir, script_name = os.path.split(sys.argv[0])

    # That is just the name of the entry point though, in the bin directory
    # Do this to get the SCRIPT_DIR path to the rest of the library resources
    dir_path = os.path.dirname(os.path.realpath(__file__))
    this_dir = os.path.abspath(os.path.join(dir_path, os.pardir))

    G.WORKSPACE = os.environ.get('WORKSPACE', 'Unknown')
    if G.WORKSPACE == 'Unknown':
        print('The Jenkins WORKSPACE variable is not set.')
        print('How can that be??')
        sys.exit(E.VARIABLE_NOT_SET)

    is_created = False
    while not is_created:
        G.START_TIME = time.strftime('%Y-%m-%d_%H.%M.%S', time.gmtime())
        G.TEMP_DIR = G.WORKSPACE + '/tmp/' + G.START_TIME

        if os.path.exists(G.TEMP_DIR):
            time.sleep(1)
        # It means another instance of this process was
        # started at the same time.  Give it a chance to
        # get out of here, and create a temp_dir with a
        # different timestamp.
        else:
            os.makedirs(validate_temp_dir_path(G.TEMP_DIR))
            if not os.path.exists(G.TEMP_DIR):
                print('Failed to make G.TEMP_DIR', G.TEMP_DIR)
                sys.exit(6)
            else:
                is_created = True

    G.SCRIPT_DIR = this_dir  # set from a local variable to satisfy Veracode
    G.SCRIPT_NAME = script_name

    G.LOG_FILENAME = G.TEMP_DIR + '/' + G.SCRIPT_NAME + '.' + G.START_TIME + '.re.log'

    setup_logging(G.LOG_FILENAME)

    G.SYSTEM_OS = platform.system()

    G.USERID = ''
    try:
        G.USERID = subprocess.check_output("echo $(whoami)", shell=True)
        G.USERID = G.USERID.strip()
        G.USERID = G.USERID.decode('utf-8')

    except Exception:
        getpass.getuser()
