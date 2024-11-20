# pylint: disable=C0209           # Don't require formtted strings

import os
import stat
import subprocess
import sys

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G
from un_re.print_msg import print_msg


# ===============================================================================
def dreml_list_files_by_sha(sha, sha_dir):
    if not os.path.exists(sha_dir):
        print_msg('ERROR: The sha_dir is not found.')
        G.LOGGER.error((' ' * 15) + 'How can that be?')
        G.LOGGER.error((' ' * 15) + 'Tried to find: {0}'.format(sha_dir))

    temp_dir = G.TEMP_DIR + '/sha'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    log_filename = temp_dir + '/{0}.re.log'.format(sha)

    bash_file = G.SCRIPT_DIR + '/un_re/shell_scripts/dreml_list_files_by_sha.bash'
    os_command = '{0} -s {1} -d {2} -l {3}'.format(
        bash_file,
        sha,
        sha_dir,
        log_filename)
    try:
        sys.stdout.flush()  # Always flush the log-file
        # output before calling a system function.

        old_perms = os.stat(bash_file)
        os.chmod(bash_file, old_perms.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error('Child was terminated by signal', -ret)
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)
        elif ret > 0:
            explained = False
            with open(log_filename, 'r', encoding='utf-8') as log_file:
                for line in log_file.readlines():
                    if line.find('unknown revision') > -1:
                        explained = True
                        break

            if explained:
                print_msg(f'Notice:  It appears this SHA is no longer part of the history: {sha}')
                ret = 0

            else:
                print_msg('ERROR:   Unable to list the git diff-tree for sha: {0}'.format(sha))
                G.LOGGER.error('')
                G.LOGGER.error('Current Working Directory: {0}'.format(os.getcwd()))

                with open(log_filename, 'r', encoding='utf-8') as log_file:
                    for line in log_file.readlines():
                        G.LOGGER.error(line.rstrip())

            return ret, log_filename
        else:
            return ret, log_filename

    except OSError as e:
        print_msg('OS ERROR: Unable to list the git diff-tree for sha: {0}'.format(sha))
        print_msg('Exception: {0}'.format(e))
        sys.exit(E.OS_ERROR)
