import os
import platform
import socket
import sys

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G

from un_re.authorize_UN_RE import authorize_UN_RE


# ======== ========= ========= ========= ========= ========= ========= ==========
def print_startup_messages(startup_message):
    G.LOGGER.info('=' * 88)
    G.LOGGER.info(startup_message)

    G.LOGGER.info(f'               Started at {G.START_TIME}')

    host = socket.gethostname()
    G.LOGGER.info(f'               Running on host {host}')

    G.LOGGER.info(f'               Running as {G.USERID}')

    G.LOGGER.info(f'               Running script {G.SCRIPT_NAME}')
    G.LOGGER.info(f'               Running python {platform.python_version()}')
    G.LOGGER.info(f'               Running from directory {G.SCRIPT_DIR}')

    G.LOGGER.info('')

    authorize_UN_RE()

    G.LOGGER.info(f'WORKSPACE    = {G.WORKSPACE}')

    # Always make sure the INI file exists.
    if len(G.INI_FILENAME) > 0:
        if not os.path.exists(G.INI_FILENAME):
            G.LOGGER.error('The Rules_Engine.ini file is not found.')
            G.LOGGER.error(f'Tried to find {G.INI_FILENAME}')
            sys.exit(E.INI_FILENAME_NOT_FOUND)
    else:
        G.LOGGER.error('No INI filename was specified.')
        sys.exit(E.INI_FILENAME_NOT_FOUND)

    temp_dir = G.TEMP_DIR.replace(G.WORKSPACE, '$WORKSPACE')
    G.LOGGER.info(f'TEMP_DIR     = {temp_dir}')

    location = G.LOG_FILENAME.replace(G.TEMP_DIR, '$TEMP_DIR')
    G.LOGGER.info(f'LOG_FILE     = {location}')
