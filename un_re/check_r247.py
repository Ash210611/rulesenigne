# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_bad_characters import check_for_bad_characters
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r247():
    '''
    Check table comments for bad characters
    '''

    G.RULE_ID = 'r247'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0

    for G.TABLE_COMMENT in G.TABLE_COMMENTS:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_COMMENT.table_name_upper):
            continue

        if G.TABLE_COMMENT.comment_txt is None:
            # If the table comment is completely missing, that
            # will be checked by r241
            continue

        msg = check_for_bad_characters(G.TABLE_COMMENT.comment_txt)

        if msg != '':
            num_findings += 1

            report_firm_finding(
                object_type_nm='table comment',
                object_nm=G.TABLE_COMMENT.table_name_upper,
                severity=G.RULES[G.RULE_ID].severity,
                message="The {0} table comment should not contain {1}.".format(
                    G.TABLE_COMMENT.table_name_upper,
                    msg),
                class_object=G.TABLE_COMMENT)
            if G.VERBOSE:
                indent_info('Table comment: {0}'.format(
                    G.TABLE_COMMENT.comment_txt))

    if num_findings > 1:
        indent_info('Notice       : Found {0} table comments with bad characters.'.format(num_findings))
    elif num_findings == 1:
        indent_info('Notice       : Found {0} table comments with bad characters.'.format(num_findings))
    elif G.VERBOSE:
        indent_debug('Good         : Found no table comments with bad characters.')

    return 0
