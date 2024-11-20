# pylint: disable=C0209           # Don't require formtted strings
# pylint: disable=C0301           # Allow a longer line

import re
import unicodedata

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent import indent
from un_re.print_msg import report_firm_finding


# ===============================================================================
def remove_control_characters(s):
    '''
    Adapted from: https://stackoverflow.com/questions/4324790/removing-control-characters-from-a-string-in-python
    '''

    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")


# ===============================================================================
def check_r416_readlines(file_obj):
    passed = True

    with open(file_obj.input_filename, 'r', encoding='utf-8') as in_file:

        line_num = 0
        for line in in_file.readlines():
            line_num += 1
            num_control_characters = len(re.findall('[\x80-\xFF]', line))

            if num_control_characters > 0:
                passed = False

                report_firm_finding(
                    object_type_nm='FILE',
                    object_nm='{0}, Line {1}'.format(
                        file_obj.input_filename,
                        line_num),
                    severity=G.RULES[G.RULE_ID].severity,
                    message='Line {0} has one or more control characters on it:'.format(line_num),
                    class_object=file_obj)

                for i in range(0, len(line), 65):
                    clean_line = remove_control_characters(line[i:i + 65])

                    # Testing shows that is not enough to avoid this error though:
                    # UnicodeEncodeError: 'ascii' codec can't encode character u'\xa0' in position...
                    clean_line = clean_line.encode('ascii', 'ignore').decode('ascii')
                    # Adapted from: https://stackoverflow.com/questions/9942594/unicodeencodeerror-ascii-codec-cant-encode-character-u-xa0-in-position-20
                    indent(clean_line)

    return passed


# ===============================================================================
def check_r416(input_filename=None):
    G.RULE_ID = 'r416'

    # -----------------------------------------------------------------------
    if input_filename is None:
        # This rule is being called from check_all_rules(), which checks
        # individual objects rather than the whole file.

        # The process_files function will specify the file when for this
        # is right for this to be checked.
        return 0

    if check_for_rule_exception(G.RULE_ID):
        return 0

    # -----------------------------------------------------------------------
    for G.FILE_OBJ in G.INPUT_FILES:
        # Failing to match one would be unthinkable.
        if G.FILE_OBJ.input_filename == input_filename:
            break

    if not G.FILE_OBJ.is_utf8_readable:
        return -1

    # -----------------------------------------------------------------------
    # Check the rule now that the prerequisites are passed.
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    passed = check_r416_readlines(G.FILE_OBJ)

    if G.VERBOSE:
        if passed:
            G.LOGGER.debug('               Good         : No control characters were found.')

    return 0
