# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent import indent
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def dreml_check_if_is_invalid():
    """
    All create-table commands checked by the DML Rules Engine must either
    be Volatile or be an ERR database.

    This finding has severity=ERROR, regardless of the rule_severities.lst
    settings, because permanent tables should be created by the
    Liquibase Apply phase, not by ETL.
    """

    found_an_issue = False

    if not re.search('VOLATILE', G.TABLE_STRUCTURE.sql_stmt_txt, re.IGNORECASE) and \
            not re.search('ERR', G.TABLE_STRUCTURE.database_base_upper):
        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            severity='ERROR',
            message='Table {0} must either be Volatile, or in an ERR database'.format(
                G.TABLE_STRUCTURE.table_name_upper),
            class_object=G.TABLE_STRUCTURE)

        found_an_issue = True

    return found_an_issue


# ===============================================================================
def check_r510():
    G.RULE_ID = 'r510'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_tables_w_an_issue = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if G.TABLE_STRUCTURE.command_type not in (
                'CREATE TABLE'
                'CREATE TABLE AS SELECT'):
            continue

        if dreml_check_if_is_invalid():
            num_tables_w_an_issue += 1

    if num_tables_w_an_issue > 1:
        indent_info('Notice       : {0} ETL Create Table statements have a location issue.'.format(
            num_tables_w_an_issue))

    elif num_tables_w_an_issue == 1:
        indent_info('Notice       : 1 ETL Create Table statement has a location issue.')

    elif G.VERBOSE:
        indent('Good         : No ETL Create Table statements have a location issue.')
