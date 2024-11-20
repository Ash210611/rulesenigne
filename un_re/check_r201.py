# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r201_for_1_column_comment(column_comment):
    found_an_issue = False

    this_object_nm = '{0}.{1}.{2}'.format(
        column_comment.database_base_upper,
        column_comment.table_name_upper,
        column_comment.column_name_upper)

    if not column_comment.comment_txt:  # if len (column_comment.comment_txt) ==  0
        found_an_issue = True

        report_adjustable_finding(
            object_type_nm='COLUMN COMMENT',
            object_nm=this_object_nm,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='Column {0} has a zero-length comment, which is not long enough.'.format(
                this_object_nm),
            adjusted_message='Accepting zero-length comment for column {0} in ruleset {1}'.format(
                this_object_nm,
                column_comment.ruleset),
            class_object=column_comment)

    else:
        column_comment.comment_txt = column_comment.comment_txt.strip()
        if not column_comment.comment_txt:  # if len (column_comment.comment_txt) == 0
            found_an_issue = True

            report_adjustable_finding(
                object_type_nm='COLUMN COMMENT',
                object_nm=this_object_nm,
                normal_severity=G.RULES[G.RULE_ID].severity,
                normal_message='Column {0} has a blank comment.'.format(
                    this_object_nm),
                adjusted_message='Accepting blank comment for column {0} in ruleset {1}'.format(
                    this_object_nm,
                    G.TABLE_STRUCTURE.ruleset),
                class_object=column_comment)

    return found_an_issue


# ===============================================================================
def check_r201_column_comments():
    num_issues = 0

    # Check that every comment is non-blank
    for column_comment in G.COLUMN_COMMENTS:

        if check_r201_for_1_column_comment(column_comment):
            num_issues += 1

    return num_issues


# ===============================================================================
def check_r201_1_table_column():
    found_the_comment = False
    for column_comment in G.COLUMN_COMMENTS:

        if column_comment.database_base_upper == G.TABLE_STRUCTURE.database_base_upper and \
                column_comment.table_name_upper == G.TABLE_STRUCTURE.table_name_upper and \
                column_comment.column_name_upper == G.COLUMN_ELEMENT.name_upper:
            found_the_comment = True
            break

    if not found_the_comment:
        this_object_nm = '{0}.{1}.{2}'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper,
            G.COLUMN_ELEMENT.name_upper)

        report_adjustable_finding(
            object_type_nm='COLUMN COMMENT',
            object_nm=this_object_nm,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='No comment was found for this column: {0}.'.format(
                this_object_nm),
            adjusted_message='Accepting missing comment for column {0} in ruleset {1}'.format(
                this_object_nm,
                G.TABLE_STRUCTURE.ruleset),
            class_object=G.TABLE_STRUCTURE)

        return 1

    return 0


# ===============================================================================
def check_r201_table_columns():
    num_issues = 0

    for G.COLUMN_ELEMENT in G.TABLE_STRUCTURE.column_elements:
        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper, G.COLUMN_ELEMENT.name_upper):
            continue

        num_issues += check_r201_1_table_column()

    return num_issues


# ===============================================================================
def check_r201_tables():
    num_issues = 0

    # Also check that every column has a comment for it.
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:
        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        num_issues += check_r201_table_columns()

    return num_issues


# ===============================================================================
def check_r201():
    G.RULE_ID = 'r201'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # print (G.TABLE_STRUCTURES)
    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_issues = check_r201_column_comments()

    num_issues += check_r201_tables()

    if num_issues == 1:
        indent_info('Notice       : 1 column comment is blank.')
    elif num_issues > 1:
        indent_info('Notice       : {0} column comments are blank.'.format(num_issues))
    elif G.VERBOSE:
        indent_debug('Good         : No column comments are blank.')

    return
