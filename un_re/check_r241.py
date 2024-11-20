# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def find_table_comment(database_base_upper, table_name_upper):
    for tc in G.TABLE_COMMENTS:
        if tc.database_base_upper == database_base_upper and \
                tc.table_name_upper == table_name_upper:
            return tc.comment_txt

    return None


# ===============================================================================
def comment_has_a_corresponding_table(database_base_upper, table_name_upper):
    for ts in G.TABLE_STRUCTURES:
        if ts.database_base_upper == database_base_upper and \
                ts.table_name_upper == table_name_upper:
            return True

    return False


# ===============================================================================
def check_r241_for_1_comment():
    """
    The table comment_str must not be empty, spaces or blank.

    Note that this rule cannot be adjusted for a ruleset,
    because a ruleset applies to 1 file, and
    comments could be created in any number of files.
    """

    found_an_issue = False

    if comment_has_a_corresponding_table(
            G.TABLE_COMMENT.database_base_upper,
            G.TABLE_COMMENT.table_name_upper):
        return found_an_issue
    # comments that have a corresponding table are checked by the
    # check_r241_for_1_table function

    comment_txt = G.TABLE_COMMENT.comment_txt.strip()

    if comment_txt is None:

        found_an_issue = True

        report_firm_finding(
            object_type_nm='TABLE COMMENT',
            object_nm=G.TABLE_COMMENT.table_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='Table {0}.{1} comment is missing.'.format(
                G.TABLE_COMMENT.database_base_upper,
                G.TABLE_COMMENT.table_name_upper),
            class_object=G.TABLE_COMMENT)

    elif len(comment_txt) == 0:

        found_an_issue = True

        report_firm_finding(
            object_type_nm='TABLE COMMENT',
            object_nm=G.TABLE_COMMENT.table_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='Comment for Table {0}.{1} has zero-length, which is not long enough.'.format(
                G.TABLE_COMMENT.database_base_upper,
                G.TABLE_COMMENT.table_name_upper),
            class_object=G.TABLE_COMMENT)

    return found_an_issue


# ===============================================================================
def check_r241_for_1_table():
    """
    The table comment_str must not be empty, spaces or blank.

    Note that this rule cannot be adjusted for a ruleset,
    because a ruleset applies to 1 file, and
    comments could be created in any number of files.
    """

    found_an_issue = False

    if G.TABLE_STRUCTURE.database_base_upper == 'VOLATILE':
        # Volatile table would not need to have a table comment.
        return found_an_issue  # == return False

    if G.TABLE_STRUCTURE.command_type not in (
            'CREATE TABLE',
            'CREATE TABLE AS SELECT'):
        # Alter table commands don't need to check this.
        # The comment would have been checked when the table was created.
        return found_an_issue  # == return False

    table_comment = find_table_comment(G.TABLE_STRUCTURE.database_base_upper, G.TABLE_STRUCTURE.table_name_upper)

    if table_comment is None:

        found_an_issue = True

        report_firm_finding(
            object_type_nm='TABLE COMMENT',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='Table {0}.{1} has no comment.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper),
            class_object=G.TABLE_STRUCTURE)

    elif len(table_comment) == 0:

        found_an_issue = True

        report_firm_finding(
            object_type_nm='TABLE COMMENT',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='Table {0}.{1} has a zero-length comment, which is not long enough.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper),
            class_object=G.TABLE_STRUCTURE)
    else:
        table_comment = table_comment.strip()
        if not table_comment:
            found_an_issue = True

            report_firm_finding(
                object_type_nm='TABLE COMMENT',
                object_nm=G.TABLE_NAME,
                severity=G.RULES[G.RULE_ID].severity,
                message='Table {0}.{1} has a blank comment.'.format(
                    G.TABLE_STRUCTURE.database_base_upper,
                    G.TABLE_STRUCTURE.table_name_upper),
                class_object=G.TABLE_STRUCTURE)

    if not found_an_issue:
        if G.VERBOSE:
            G.LOGGER.debug((' ' * 15) + 'Good         : {0}.{1} table comment is not empty, blank, or spaces.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper))

    return found_an_issue


# ===============================================================================
def check_r241_for_comments():
    num_findings = 0

    for G.TABLE_COMMENT in G.TABLE_COMMENTS:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_COMMENT.table_name_upper):
            continue

        if check_r241_for_1_comment():
            num_findings += 1

    if num_findings > 1:
        indent_info('Notice       : {0} table comments were empty.'.format(num_findings))

    elif num_findings == 1:
        indent_info('Notice       : {0} table comment was empty.'.format(num_findings))


# ===============================================================================
def check_r241_for_tables():
    num_findings = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        if check_r241_for_1_table():
            num_findings += 1

    if num_findings > 1:
        indent_info('Notice       : {0} tables were missing their table comments.'.format(num_findings))

    elif num_findings == 1:
        indent_info('Notice       : {0} table was missing its table comment.'.format(num_findings))

    elif G.VERBOSE:
        indent_debug('Good         : No tables are missing their table comments.')


# ===============================================================================
def check_r241():
    """
    Every table created with a Create Table command or a CTAS command
    should have comment.

    Comments could be created on their own though, so we also check that
    every comment is not blank or empty.
    """

    G.RULE_ID = 'r241'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    check_r241_for_tables()
    check_r241_for_comments()

    return 0
