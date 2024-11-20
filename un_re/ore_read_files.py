# pylint: disable=C0209           # Don't require formtted strings
# pylint: disable=C0301           # Allow long lines

import os
import re
import sys

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G

from un_re.get_file_contents import get_file_contents


# ======== ========= ========= ========= ========= ========= ========= ==========
def ore_clean_file_contents(contents):
    # To help Antlr parse loops, change this:
    #       FOR i IN 1..SQL%BULK_EXCEPTIONS.COUNT LOOP
    # To
    #       FOR i IN 1 .. SQL%BULK_EXCEPTIONS.COUNT LOOP
    regex1 = r"(\d|\w)\.\.(\d|\w)"
    subst1 = r'\1 .. \2'

    # Do this up to 99 times (The default is 0!)
    contents = re.sub(regex1, subst1, contents, 99, re.MULTILINE)

    return contents


# ======== ========= ========= ========= ========= ========= ========= ==========
# Adapting the line counter from: https://pynative.com/python-count-number-of-lines-in-file/

# def _count_generator(reader):
# 	b = reader(1024 * 1024)
# 	while b:
# 		yield b
# 		b = reader(1024 * 1024)
#
# def count_lines (filename):
# 	with open(filename, 'rb') as fp:
# 		c_generator = _count_generator(fp.raw.read)
# 		# count each \n
# 		count = sum(buffer.count(b'\n') for buffer in c_generator)
# 	return count+1
#
# ======== ========= ========= ========= ========= ========= ========= ==========
# Adapting the line counter from: https://stackoverflow.com/questions/845058/how-to-get-the-line-count-of-a-large-file-cheaply-in-python
def count_lines(filename):
    with open(filename, "rb") as f:
        num_lines = sum(1 for _ in f)
    return num_lines


# ======== ========= ========= ========= ========= ========= ========= ==========
def ore_read_files():
    '''
    Find the files, and update the class instance with their contents.
    '''

    G.LOGGER.info('=' * 80)
    G.LOGGER.info('Reading all Oracle files...')

    for G.INPUT_FILE in G.INPUT_FILES:
        if os.path.exists(G.INPUT_FILE.input_filename):
            G.INPUT_FILE.num_lines = count_lines(G.INPUT_FILE.input_filename)
            G.LOGGER.info('        Lines: {0:5d} - Found: File {1} - {2}'.format(
                G.INPUT_FILE.num_lines,
                G.INPUT_FILE.filenum + 1,
                G.INPUT_FILE.input_filename.replace(G.WORKSPACE, '$WORKSPACE')))
        else:
            G.LOGGER.info('        Error: Cannot find file {0}- {1}'.format(
                G.INPUT_FILE.filenum + 1,
                G.INPUT_FILE.input_filename.replace(G.WORKSPACE, '$WORKSPACE')))
            sys.exit(E.FILE_NOT_FOUND)

        if G.INPUT_FILE.is_utf8_readable:
            file_contents = get_file_contents(G.INPUT_FILE.input_filename)

            G.INPUT_FILE.contents = ore_clean_file_contents(file_contents)

    G.LOGGER.info('')
