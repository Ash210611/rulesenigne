# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_bad_characters import check_for_bad_characters
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r207_for_1_column_comment(column_comment):
    found_an_issue = False

    if column_comment.comment_txt is None:
        return found_an_issue  # There are no chars to check at all.

    msg = check_for_bad_characters(column_comment.comment_txt)

    if msg != '':
        object_nm = '{0}.{1}.{2}'.format(
            column_comment.database_base_upper,
            column_comment.table_name_upper,
            column_comment.column_name_upper)

        found_an_issue = True
        report_adjustable_finding(object_type_nm='column comment',
                                  object_nm=object_nm,
                                  normal_severity=G.RULES[G.RULE_ID].severity,
                                  normal_message='The column comment for {0} should not contain {1}.'.format(
                                      object_nm,
                                      msg),
                                  adjusted_message='Accepting {0} in column comment for {1} for ruleset{2}.'.format(
                                      msg,
                                      object_nm,
                                      column_comment.ruleset),
                                  class_object=column_comment)

        indent_info(f'Found comment: {column_comment.comment_txt}')

    return found_an_issue


# ===============================================================================
def check_r207():
    G.RULE_ID = 'r207'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_issues_found = 0
    for column_comment in G.COLUMN_COMMENTS:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME,
                                    column_comment.table_name_upper, column_comment.column_name_upper):
            continue

        if check_r207_for_1_column_comment(column_comment):
            num_issues_found += 1

    if num_issues_found == 1:
        indent_info('Notice       : {0} column comment has a bad character.'.format(
            num_issues_found))
    elif num_issues_found > 1:
        indent_info('Notice       : {0} column comments have a bad character.'.format(
            num_issues_found))
    elif G.VERBOSE:
        indent_debug('Good         : No column comments have bad characters.')

    return
