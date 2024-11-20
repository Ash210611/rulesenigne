# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G

from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r260_for_1_column_name(ce):
    found_an_issue = False
    num_columns_named_this = 0
    for test_ce in G.COLUMN_ELEMENTS:
        if test_ce.position < ce.position:
            # We already counted those
            continue

        if ce.name_upper == test_ce.name_upper:
            num_columns_named_this += 1

    if num_columns_named_this > 1:
        found_an_issue = True

        key = G.TABLE_STRUCTURE.database_base_upper + '.' + \
              G.TABLE_STRUCTURE.table_name_upper + '.' + \
              G.COLUMN_ELEMENT.name_upper

        report_adjustable_finding(
            object_type_nm='COLUMN',
            object_nm=key,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='Column name {0} is specified {1} times.'.format(
                key,
                num_columns_named_this),
            adjusted_message='Accepting table name {0} specified {1} times under ruleset {2}.'.format(
                key,
                num_columns_named_this,
                G.TABLE_STRUCTURE.ruleset),
            class_object=G.TABLE_STRUCTURE)

    return found_an_issue


# ===============================================================================
def check_r260_for_1_column():
    found_an_issue = False
    G.COLUMN_ELEMENTS = G.TABLE_STRUCTURE.column_elements

    if len(G.COLUMN_ELEMENTS) == 0:
        return found_an_issue  # There are no duplicate columns if no columns

    for G.COLUMN_ELEMENT in G.COLUMN_ELEMENTS:
        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper,
                                    G.COLUMN_ELEMENT.name_upper):
            continue

        if check_r260_for_1_column_name(G.COLUMN_ELEMENT):
            found_an_issue = True

    if not found_an_issue:
        if G.VERBOSE:
            indent_debug('Good         : {0}.{1} has no duplicated column names.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper))

    return found_an_issue


# ===============================================================================
def count_num_ct_commands(database_base_upper, table_name_upper):
    """
    Count the number of Create Table commands
    """
    num_ct_commands = 0

    for table_structure in G.TABLE_STRUCTURES:
        if table_structure.command_type not in ('CREATE TABLE', 'CREATE TABLE AS SELECT'):
            # It is OK to skip Alter Table commands. It is OK for a
            # deployment to include both create-table and
            # alter-table commands
            continue

        if table_structure.database_base_upper == database_base_upper and \
                table_structure.table_name_upper == table_name_upper:
            num_ct_commands += 1

    return num_ct_commands


# ===============================================================================
def count_num_tc_commands(database_base_upper, table_name_upper):
    """
    Count the number of Comment On Table commands
    """
    num_tc_commands = 0

    for tc in G.TABLE_COMMENTS:

        if tc.database_base_upper == database_base_upper and \
                tc.table_name_upper == table_name_upper:
            num_tc_commands += 1

    return num_tc_commands


# ===============================================================================
def check_r260_for_1_table_name():
    """
    Return True if there is an issue and it fails
    Return False if there is no issue and it passes.
    """

    if G.TABLE_STRUCTURE.database_base_upper == 'VOLATILE':
        return False

    num_ct_commands = count_num_ct_commands(
        G.TABLE_STRUCTURE.database_base_upper,
        G.TABLE_STRUCTURE.table_name_upper)

    if num_ct_commands > 1:
        key = G.TABLE_STRUCTURE.database_base_upper + '.' + \
              G.TABLE_STRUCTURE.table_name_upper

        report_adjustable_finding(
            object_type_nm='TABLE',
            object_nm=key,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='Table name {0} is specified {1} times.'.format(
                key,
                num_ct_commands),
            adjusted_message='Accepting table name {0} specified {1} times under ruleset {2}.'.format(
                key,
                num_ct_commands,
                G.TABLE_STRUCTURE.ruleset),
            class_object=G.TABLE_STRUCTURE)

        return True

    return False


# ===============================================================================
def check_r260_for_1_table_comment():
    """
    Return True if there is an issue and it fails
    Return False if there is no issue and it passes.
    """

    if G.TABLE_STRUCTURE.database_base_upper == 'VOLATILE':
        return False

    num_tc_commands = count_num_tc_commands(
        G.TABLE_STRUCTURE.database_base_upper,
        G.TABLE_STRUCTURE.table_name_upper)

    if num_tc_commands > 1:
        key = G.TABLE_STRUCTURE.database_base_upper + '.' + \
              G.TABLE_STRUCTURE.table_name_upper

        report_adjustable_finding(
            object_type_nm='TABLE COMMENT',
            object_nm=key,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='Comment for table {0} is specified {1} times.'.format(
                key,
                num_tc_commands),
            adjusted_message='Accepting comment for table {0} specified {1} times under ruleset {2}.'.format(
                key,
                num_tc_commands,
                G.TABLE_STRUCTURE.ruleset),
            class_object=G.TABLE_STRUCTURE)

        return True

    return False


# ===============================================================================
def check_r260_for_1_table():
    # found_an_issue = False   # Logically does not need initialization.
    if G.TABLE_STRUCTURE.command_type in ('CREATE TABLE', 'CREATE TABLE AS SELECT'):

        if check_r260_for_1_table_name():
            return True
        # Do not check for dup columns when the whole table is duplicated.

        # ---------------------------------------------------------------
        if check_r260_for_1_table_comment():
            return True
        # If they fix that issue and retry, we'll check for
        # column dups next time.

    found_an_issue = check_r260_for_1_column()

    return found_an_issue


# ===============================================================================
def check_r260():
    G.RULE_ID = 'r260'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_table_findings = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper):
            continue

        if check_r260_for_1_table():
            num_table_findings += 1

    if num_table_findings > 1:
        indent_info('Notice       : Found {0} tables with duplication issues.'.format(num_table_findings))
    elif num_table_findings == 1:
        indent_info('Notice       : Found {0} table with a duplication issue.'.format(num_table_findings))
    elif G.VERBOSE:
        indent_debug('Good         : No tables have issues with duplication.')

    return 0
