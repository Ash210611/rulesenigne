# pylint: disable=W0702			# Don't limit the exception type

import os
import time

from un_re.print_msg import print_msg


# ======== ========= ========= ========= ========= ========= ========= ==========
def make_local_script_dir(local_script_dir):
    """
    This function checks if the local_script_dir directory exists.
    If it does not exist, it tries to create it.
    With parallel processing, another process may have created it in
    between those two steps, cause the other to fail, so this function
    will wait a second or so, then recheck and retry, for a limited
    number of tries.
    """

    if os.path.exists(local_script_dir):
        return

    succeeded = False
    num_failures = 0
    while not succeeded and num_failures < 3:
        try:
            os.makedirs(local_script_dir)
        except:
            num_failures += 1
            # print_msg ('Notice: Num failures to make subdirectory for local script: {0}.'.format (num_failures))
            # print_msg ('Failed to makedir: {0}'.format (local_script_dir))
            # print_msg ('Will recheck and retry in {0} seconds in case of parallel conflict.'.format (num_failures))
            time.sleep(num_failures)

        if os.path.exists(local_script_dir):
            succeeded = True

    if not succeeded:
        print_msg('ERROR: Failed to create subdirectory for local script.')
        print_msg((' ' * 15) + f'Failed to makedir: {local_script_dir}')
