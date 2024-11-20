# pylint: 	disable=C0209		# Don't require formatted strings.
# pylint: 	disable=R1732		# Don't require the with function

# The functions in this module are useful for removing non-printable
# characters from an input file.
# ======== ========= ========= ========= ========= ========= ========= ==========

import codecs
import inspect
import os
import stat  # for stat constants.
import subprocess
import sys
from tempfile import NamedTemporaryFile

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G
from un_re.get_file_contents import get_file_contents


# ======== ========= ========= ========= ========= ========= ========= ==========
def convert_smart_dashes(input_filename):
    # I would like to replace this with a 100% native Python function, as
    # soon as I can figure out how.   In the meantime, this is a practical
    # solution.  Ditto for the next two functions

    # Get a temporary filename
    tmp_file = NamedTemporaryFile(delete=False)
    tmp_file.close()

    bash_file = G.SCRIPT_DIR + '/un_re/shell_scripts/convert_smart_dashes.bash'
    os_command = bash_file + ' ' + input_filename + ' ' + tmp_file.name

    try:
        sys.stdout.flush()  # Always flush the log-file
        # output before calling a
        # system function.

        old_perms = os.stat(bash_file)
        os.chmod(bash_file, old_perms.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error('Child was terminated by signal {0}'.format(-ret))
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)
        elif ret > 0:
            G.LOGGER.info('Subprocess exited with code {0}'.format(ret))

    except OSError as e:
        G.LOGGER.error('Failed to run command in File: {0}, Line: {1}\n{2}'.format(
            os.path.basename(__file__),
            inspect.stack()[0][2],
            e))
        sys.exit(45)


# ======== ========= ========= ========= ========= ========= ========= ==========
def convert_smart_quotes(input_filename):
    file_contents = get_file_contents(input_filename)
    new_file_contents = file_contents.replace('\u201c', '"')
    new_file_contents = new_file_contents.replace('\u201d', '"')

    if file_contents != new_file_contents:
        with open(input_filename, 'w', encoding='utf-8') as in_file:
            in_file.write(new_file_contents)
        G.LOGGER.info('               Notice: Replaced smart quotes with Ascii quotes.')


# ======== ========= ========= ========= ========= ========= ========= ==========
def convert_smart_apostrophes_v2(input_filename):
    """
    Replace smart quotes with simple Ascii quotes

    This sequence was found in the following command
    COMMENT ON COLUMN RXRDS_CLM_DRUG_MV.FDA_DRUG_EFCY_CD IS
        'The code specifying the FDA rating of therapeutic equivalence of generic drug products to an innovator drug.
    EX:
    A =Codes that begin with ''A'' are considered pharmaceutically equivalent to other products
    B =Codes that begin with ''B'' are not considered';

    If you try to paste that from GitLab into TD Studio, Teradata will
    simply drop it, so the algorithm below will drop it too.
    """

    file_contents = get_file_contents(input_filename)
    new_file_contents = file_contents.replace('\u2018', "'")
    new_file_contents = new_file_contents.replace('\u2019', "'")
    # new_file_contents = new_file_contents.replace ('\u0092', "''")

    if file_contents != new_file_contents:
        with open(input_filename, 'w', encoding='utf-8') as in_file:
            in_file.write(new_file_contents)
        G.LOGGER.info('               Notice: Replaced smart apostrophes with Ascii apostrophes.')


# ======== ========= ========= ========= ========= ========= ========= ==========
def display_unicode_values():
    # With Python 3, This code will help me figure out the Unicode values
    with open(G.TEMP_DIR + '/junk.rot',
              'r', encoding='utf-8') as in_file:
        for ch in iter(lambda: in_file.read(1), ''):
            print('ch = {0}, ord(ch) = {1}, Unicode = U+{1:04x}'.format(ch, ord(ch)))


# ======== ========= ========= ========= ========= ========= ========= ==========
def remove_possessive(input_filename):
    """
    Remove the possessive punctuation mark sequence 194+146
    """

    # This sequence was found in the following command
    # COMMENT ON COLUMN RXRDS_CLM_DRUG_MV.GCN_SEQ_NUM IS \
    #	'Generic code number's field that further delineates the GCN number.';
    # I can't show the actual command here, as Python
    # reports 'SyntaxError: Non-ASCII character'

    # If you try to paste that from GitLab into TD Studio, Teradata will
    # simply drop it, so the algorithm below will drop it too.

    # noinspection PyUnusedLocal
    prev_ch = ''
    new_file_contents = ''
    removed_at_least_one = False
    with open(input_filename, 'r', encoding='utf-8') as in_file:
        for ch in iter(lambda: in_file.read(1), ''):
            if ord(ch) == 194:
                prev_ch = ch
                ch = in_file.read(1)
                if ord(ch) == 146:
                    removed_at_least_one = True
                else:
                    new_file_contents += prev_ch
                    new_file_contents += ch
            else:
                new_file_contents += ch

    if removed_at_least_one:
        with open(input_filename, 'w', encoding='utf-8') as in_file:
            in_file.write(new_file_contents)
        G.LOGGER.info('               Notice: Removed irregular possessive punctuation mark 194+146')


# ======== ========= ========= ========= ========= ========= ========= ==========
def remove_carriage_returns(input_filename):
    file_contents = get_file_contents(input_filename)

    new_file_contents = file_contents.replace('\r', '')

    if file_contents != new_file_contents:
        with codecs.open(input_filename, 'w', encoding='utf-8') as wfile:
            wfile.write(new_file_contents)
        G.LOGGER.info('               Notice: Removed extra carriage return characters from this file.')


# ======== ========= ========= ========= ========= ========= ========= ==========
def remove_nulls(input_filename):
    file_contents = get_file_contents(input_filename)

    new_file_contents = file_contents.replace('\x00', '')

    if file_contents != new_file_contents:
        with codecs.open(input_filename, 'w', encoding='utf-8') as wfile:
            wfile.write(new_file_contents)
        G.LOGGER.info('               Notice: Removed null characters from this file.')


# ======== ========= ========= ========= ========= ========= ========= ==========
def remove_other_control_chars(input_filename):
    """
    Granted, that is not the most efficient way to remove control characters,
    but it provides the most accurate feedback to the user about which
    specific control characters were replaced, and it replaces only the ones
    we have actually ever seen so far.
    """

    # This used to be the old list of char_nums
    #	[205, 223, 224, 225, 226, 240, 267, 273, 277, 302, 357, 376, 377]
    # Python needs them to be decimal for the following algorithm to work
    # Here is the decimal list
    #	[133, 147, 148, 149, 150, 160, 183, 187, 191, 194, 239, 254, 255]

    # I tried using replace, and re.sub, and they would not accomplish the job

    for decimal_char_num in [133, 147, 148, 149, 150, 160, 183, 187, 191, 194, 239, 254, 255]:
        new_file_contents = ''
        replaced_at_least_one = False
        with open(input_filename, 'r', encoding='utf-8', errors='replace') as in_file:
            bytes_read = in_file.read()

            for ch in bytes_read:
                # print ('ch = {0}'.format (ch))
                if ord(ch) == decimal_char_num:
                    ch = ' '
                    replaced_at_least_one = True

                new_file_contents += ch

        if replaced_at_least_one:
            with open(input_filename, 'w', encoding='utf-8') as in_file:
                in_file.write(new_file_contents)

            G.LOGGER.info(
                '               Notice: Replaced char %d with space character in this file.' % decimal_char_num)


# ======== ========= ========= ========= ========= ========= ========= ==========
def clean_file(input_filename):
    """
    Clean the local copy of the Input SQL file, by removing control
    characters from the file.
    """

    # convert_smart_dashes 		(input_filename)
    convert_smart_quotes(input_filename)
    convert_smart_apostrophes_v2(input_filename)
    remove_nulls(input_filename)
    remove_carriage_returns(input_filename)
    remove_other_control_chars(input_filename)
# display_unicode_values	() # comment this out when finished with it.

# if G.VERBOSE:
# 	G.LOGGER.debug ((' ' * 15) + 'Done cleaning the input filename...')
