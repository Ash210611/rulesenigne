# pylint: disable=C0209           # Don't require formtted strings

import os
import shutil
import time

import un_re.global_shared_variables as G


# ===============================================================================
def cleanup_old_tmp_directories():
    """
    Adapted from
    https://stackoverflow.com/questions/39456318/delete-directories-older-than-x-days/39456407
    """

    path = G.SCRIPT_DIR + '/tmp'
    G.LOGGER.info('Checking old tmp directories under: {0}'.format(
        path.replace(G.SCRIPT_DIR, '$SCRIPT_DIR')))

    now = time.time()
    old = now - (G.NUM_DAYS_TO_SAVE_LOG_FILES * 24 * 60 * 60)

    # for root, dirs, files in os.walk...
    for root, dirs, _ in os.walk(path, topdown=False):
        for this_dir in dirs:
            dir_path = root + os.sep + this_dir
            dir_time = os.stat(dir_path).st_ctime
            age = dir_time - old

            if age < 0:
                G.LOGGER.info('Removing old tmp directory: {0}'.format(
                    dir_path.replace(G.SCRIPT_DIR, '$SCRIPT_DIR')))
                # G.LOGGER.info ( 'Age: {0}'.format (int (age)) )
                shutil.rmtree(dir_path)
            else:
                # G.LOGGER.info ( 'Keeping  old tmp directory: {0}'.format (
                # 	dir_path.replace (G.SCRIPT_DIR, '$SCRIPT_DIR')))
                pass
