# pylint: disable=C0209			# Don't require formatted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_g001_for_1_file():
    if not G.INPUT_FILE.is_utf8_readable:
        report_firm_finding(
            object_type_nm='FILE',
            object_nm=G.INPUT_FILE.input_filename_rel,
            severity=G.RULES[G.RULE_ID].severity,
            message='UTF-8 error found in this file: {0}.'.format(
                G.INPUT_FILE.input_filename_rel),
            class_object=G.INPUT_FILE)

    return G.INPUT_FILE.is_utf8_readable


# ===============================================================================
def check_g001():
    """
    The file must be able to be opened with UTF-8
    """

    G.RULE_ID = 'g001'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        # This rule g003 applies more to a DDL file, and not a table or
        # colun name.   If you can't parse the SQL statement, you can't
        # really tell what table or column names it works on.
        return 0

    num_found = 0

    for G.INPUT_FILE in G.INPUT_FILES:

        if not check_g001_for_1_file():
            num_found += 1

    num_files = len(G.INPUT_FILES)

    if num_found > 1:
        indent_info('Notice       : Found {0} UTF-8 errors in {1} files.'.format(num_found, num_files))
    elif num_found == 1:
        if num_files == 1:
            indent_info('Notice       : Found {0} UTF-8 error in 1 file.'.format(num_found))
        else:
            indent_info('Notice       : Found {0} UTF-8 error in {1} files.'.format(num_found, num_files))
    elif G.VERBOSE:
        if num_files == 1:
            indent_debug('Good         : No UTF-8 errors found in {0} file.'.format(num_files))
        else:
            indent_debug('Good         : No UTF-8 errors found in {0} files.'.format(num_files))

    return 0
