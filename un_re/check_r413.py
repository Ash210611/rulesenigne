# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.KNOWN_DB as A
import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r413_for_1_view():
    found_an_issue = False
    if G.VIEW_STRUCTURE.database_base_upper == 'UNKNOWN':

        found_an_issue = True

        report_firm_finding(
            object_type_nm='VIEW',
            object_nm=G.VIEW_STRUCTURE.view_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='View {0} has no database qualifier.'.format(
                G.VIEW_STRUCTURE.view_name_upper),
            class_object=G.VIEW_STRUCTURE)

        indent_info('Based on this statement: ')
        for line in G.VIEW_STRUCTURE.sql_stmt_txt.split('\n'):
            indent_info(f'{line}')

    elif G.RULES_ENGINE_TYPE == 'TERADATA_DDL':
        # Make sure the database name is in the list of Known Databases
        found_known_db = False
        for known_db in A.KNOWN_DB:
            if re.search(known_db.database_base,
                         G.VIEW_STRUCTURE.database_base_upper, re.IGNORECASE):
                found_known_db = True
                break

        if not found_known_db:

            found_an_issue = True

            report_firm_finding(
                object_type_nm='VIEW',
                object_nm=G.VIEW_STRUCTURE.view_name_upper,
                severity=G.RULES[G.RULE_ID].severity,
                message='View {0}.{1} is not qualified with a known DB.'.format(
                    G.VIEW_STRUCTURE.database_base_upper,
                    G.VIEW_STRUCTURE.view_name_upper),
                class_object=G.VIEW_STRUCTURE)

            indent_info('Based on this statement: ')
            for line in G.VIEW_STRUCTURE.sql_stmt_txt.split('\n'):
                indent_info(f'{line}')

    if not found_an_issue:
        if G.VERBOSE:
            indent_debug('Good         : View {0}.{1} has a database qualifier.'.format(
                G.VIEW_STRUCTURE.database_base_upper,
                G.VIEW_STRUCTURE.view_name_upper))

    return found_an_issue


# ===============================================================================
def check_r413():
    """
    Check that each create-view command has a database qualifier
    This is not done for create-table commands, only for create/replace view
    commands.
    """

    G.RULE_ID = 'r413'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if G.RULES_ENGINE_TYPE not in (
            'TERADATA_DDL',
            'REDSHIFT'):
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0

    for G.VIEW_STRUCTURE in G.VIEW_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.VIEW_STRUCTURE.view_name_upper):
            continue

        if check_r413_for_1_view():
            num_findings += 1

    if num_findings > 1:
        indent_info('Notice       : {0} views are missing a database qualifier.'.format(num_findings))
    elif num_findings == 1:
        indent_info('Notice       : {0} view is missing a database qualifier.'.format(num_findings))
    elif G.VERBOSE:
        indent_debug('Good         : All views have a database qualifier.')

    return 0
