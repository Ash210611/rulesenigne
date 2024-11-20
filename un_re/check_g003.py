# pylint: disable=C0209			# Don't require formatted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_g003_for_1_file():
    if G.FILE_OBJ.has_a_syntax_error:
        report_adjustable_finding(
            object_type_nm='FILE',
            object_nm=G.FILE_OBJ.input_filename_rel,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='Syntax error found in this file: {0}.'.format(
                G.FILE_OBJ.input_filename_rel),
            adjusted_message='Allowing syntax error in this file: {0}.'.format(
                G.FILE_OBJ.input_filename_rel),
            class_object=G.FILE_OBJ)

    return G.FILE_OBJ.has_a_syntax_error


# ===============================================================================
def check_g003():
    """
    No syntax errors must be found.
    """

    G.RULE_ID = 'g003'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        # This rule g003 applies more to a DDL file, and not a table or
        # colun name.   If you can't parse the SQL statement, you can't
        # really tell what table or column names it works on.
        return

    num_found = 0

    for G.FILE_OBJ in G.INPUT_FILES:

        filename_base = G.FILE_OBJ.input_filename_rel.split('/')[-1]

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, filename_base):
            # This slightly overloads that function by putting a
            # filename into a tablename field.   It is a reasonable
            # approximation since we usually have 1 table per file.
            continue

        if check_g003_for_1_file():
            num_found += 1

    num_files = len(G.INPUT_FILES)

    if num_found > 1:
        indent_info('Notice       : Found {0} syntax errors in {1} files.'.format(num_found, num_files))
    elif num_found == 1:
        if num_files == 1:
            indent_info('Notice       : Found {0} syntax error in {1} file.'.format(num_found, num_files))
        else:
            indent_info('Notice       : Found {0} syntax error in {1} files.'.format(num_found, num_files))
    elif G.VERBOSE:
        if num_files == 1:
            indent_debug('Good         : No syntax errors found in {0} file.'.format(num_files))
        else:
            indent_debug('Good         : No syntax errors found in {0} files.'.format(num_files))

    return
