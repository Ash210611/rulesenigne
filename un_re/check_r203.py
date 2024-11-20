# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r203_for_1_column_comment(column_comment):
    found_an_issue = False

    if column_comment.comment_txt is None:
        return found_an_issue  # return False, it is not too long.

    comment_len = len(column_comment.comment_txt)

    this_object_nm = '{0}.{1}.{2}'.format(
        column_comment.database_base_upper,
        column_comment.table_name_upper,
        column_comment.column_name_upper)

    if comment_len > 255:
        found_an_issue = True
        report_firm_finding(
            object_type_nm='COLUMN COMMENT',
            object_nm=this_object_nm,
            severity=G.RULES[G.RULE_ID].severity,
            message='{0} column comment has {1} bytes, which is too long'.format(
                this_object_nm,
                comment_len),
            class_object=column_comment)

        indent_info('Column Comment: {0}...'.format(column_comment.comment_txt[:62]))

    return found_an_issue


# ===============================================================================
def check_r203():
    G.RULE_ID = 'r203'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # No need to check for a rule exception, as this is a hard limit.

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_issues = 0
    for column_comment in G.COLUMN_COMMENTS:

        if check_r203_for_1_column_comment(column_comment):
            num_issues += 1

    if num_issues == 1:
        indent_info('Notice       : 1 column comment is longer than 255.')

    elif num_issues > 1:
        indent_info('Notice       : {0} column comments are longer than 255.'.format(
            num_issues))

    elif G.VERBOSE:
        indent_debug('Good         : No column comments are too long.')

    return
