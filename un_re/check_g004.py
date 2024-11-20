# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_g004_for_1_table():
    found_an_issue = False
    if G.TABLE_STRUCTURE.database_base_upper == 'UNKNOWN':

        found_an_issue = True

        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message=f'No Database Base was recognized for table {G.TABLE_STRUCTURE.table_name_orig}.',
            class_object=G.TABLE_STRUCTURE)

    elif G.VERBOSE:
        indent_debug('Good         : {0} is the database context for table {1}'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_orig))

    return found_an_issue


# ===============================================================================
def check_g004_for_1_view():
    found_an_issue = False
    if G.VIEW_STRUCTURE.database_base_upper == 'UNKNOWN':

        found_an_issue = True

        report_firm_finding(
            object_type_nm='VIEW',
            object_nm=G.VIEW_STRUCTURE.view_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='No Database Base was recognized for view {0}.'.format(
                G.VIEW_STRUCTURE.view_name_upper),
            class_object=G.VIEW_STRUCTURE)

    elif G.VERBOSE:
        indent_debug('Good         : A database context is found for view {0}.'.format(G.VIEW_STRUCTURE.view_name_orig))

    return found_an_issue


# ===============================================================================
def check_g004_for_1_column(column_comment):
    found_an_issue = False
    this_object_nm = f'{column_comment.table_name_upper}.{column_comment.column_name_upper}'

    if column_comment.database_base_upper == 'UNKNOWN':
        found_an_issue = True
        report_firm_finding(
            object_type_nm='COLUMN',
            object_nm=this_object_nm,
            severity=G.RULES[G.RULE_ID].severity,
            message=f'No Database Base was recognized for column {this_object_nm}.',
            class_object=column_comment)

    # elif G.VERBOSE:
    # 	indent_debug ('Good         : {0} is the database context for {1}'.format (
    # 		column_comment.database_base_upper,
    # 		this_object_nm))
    # Too much!

    return found_an_issue


# ===============================================================================
def check_g004():
    """
    A database context must be recognized.

    """

    G.RULE_ID = 'g004'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))
    num_found = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        if check_g004_for_1_table():
            num_found += 1

    for G.VIEW_STRUCTURE in G.VIEW_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.VIEW_STRUCTURE.view_name_upper):
            continue

        if check_g004_for_1_view():
            num_found += 1

    for column_comment in G.COLUMN_COMMENTS:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, column_comment.table_name_upper):
            continue

        if check_g004_for_1_column(column_comment):
            num_found += 1

    if G.VERBOSE and num_found == 0:
        indent_debug('Good         : A database context is found for all tables, views, and comments.')

    return
