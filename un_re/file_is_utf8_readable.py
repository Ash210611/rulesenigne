# pylint: 	disable=C0209		# Don't require formatted strings.
# pylint: 	disable=R1732		# Don't require the with function

# The functions in this module are useful for removing non-printable
# characters from an input file.
# ======== ========= ========= ========= ========= ========= ========= ==========

import os

import un_re.global_shared_variables as G
from un_re.print_msg import print_and_log_msg
from un_re.print_msg import print_msg


# ======== ========= ========= ========= ========= ========= ========= ==========
def file_is_utf8_readable(filename):  # pylint: disable=consider-using-with

    is_utf8_readable = False

    if not os.path.isfile(filename):
        print_msg("ERROR.         This filename is not found.")
        G.LOGGER.error('Tried to find: {0}'.format(filename))
        G.LOGGER.error('')
        return is_utf8_readable
    # Don't we already know the file is found?

    try:
        input_file = open(filename, 'r', encoding='utf-8')
        input_file.read()
        input_file.close()

        is_utf8_readable = True

    except UnicodeDecodeError:
        is_utf8_readable = False

        print_and_log_msg('ERROR-g001   : This file contains a character not encodable by utf-8')

        replaced_bytes = open(filename, 'r', encoding='utf-8', errors='replace').read()
        binary_bytes = open(filename, 'rb').read()
        array_len = len(binary_bytes)
        for i in range(array_len):
            if binary_bytes[i] != ord(replaced_bytes[i]):
                G.LOGGER.error('Around byte {0}'.format(i))
                G.LOGGER.error('Here are 30 bytes of context around that position:')

                if i > 30:
                    start = i - 30
                else:
                    start = 0

                if i < array_len - 30:
                    stop = i + 30
                else:
                    stop = array_len

                context = replaced_bytes[start: stop]
                # Must decode to ascii because the
                # errors=replace doesn't clean enough
                # to avoid another UnicodeDecodeError
                context = context.encode('ascii', 'ignore').decode('ascii')

                G.LOGGER.error(f'{context}')
                G.LOGGER.error('Please edit and retry.')
                G.LOGGER.error('')
                is_utf8_readable = False

    return is_utf8_readable
