# pylint: disable=C0209			# Don't require formatted strings

import os
import re
import subprocess

import un_re.global_shared_variables as G
from un_re.fprint import fprint


# ===============================================================================
# For a blog about the Repo object, see:
# https://gitpython.readthedocs.io/en/stable/tutorial.html
# https://stackoverflow.com/questions/9774972/trying-to-execute-git-command-using-python-script

# ===============================================================================
def get_comt_user_id(input_filename):
    comt_user_id = 'UNKNOWN'  # Default value to start with.

    git_log_response = ''

    command = 'git log -n 2 {0}'.format(os.path.basename(input_filename))

    try:
        with subprocess.Popen(
                command,
                cwd=os.path.dirname(input_filename),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8') as pr:

            # (git_log_response, error) = pr.communicate()
            (git_log_response, _) = pr.communicate()

            # print "Error : " + str(error)
            for line in git_log_response.split('\n'):
                if re.search('Author:', line):
                    comt_user_id = line.split(':')[1]
                    # print (comt_user_id)
                    break
    except:
        err_filename = '{0}/git_log.err'.format(G.WORKSPACE)
        with open(err_filename, 'w', encoding='utf-8') as err_file:
            fprint(err_file, f'Input_filename  : {input_filename}')
            fprint(err_file, f'Command         : {command}')
            fprint(err_file, f'Git log_response: {git_log_response}')
        # print ('Error           : {0}'.format (error))
        raise

    return comt_user_id
