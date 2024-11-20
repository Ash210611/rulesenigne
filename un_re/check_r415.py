# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.KNOWN_DB as A
import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.binary_search import binary_search
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r415_if_table_on_exception_list(pattern):
    found_an_issue = False

    comparison_table = C.MultisetBaseTable(G.TABLE_STRUCTURE.table_name_upper, '')

    # Check if this table is on the exception list.
    found_exception = binary_search(G.MULTISET_BASE_TABLES, comparison_table)

    if found_exception:
        indent_info('Notice       : Table {0}.{1} is allowed to be Multiset by exception'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper))

    else:
        found_an_issue = True

        report_adjustable_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='BASE table {0}.{1} should not be MULTISET.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper),
            adjusted_message='Accepting MULTISET table {0}.{1} in ruleset {2}'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.TABLE_STRUCTURE.ruleset),
            class_object=G.TABLE_STRUCTURE)

        # Print that line for context
        for line in G.TABLE_STRUCTURE.sql_stmt_txt.split('\n'):
            if pattern.search(line):
                indent_info(line)

        G.LOGGER.info('')

    return found_an_issue


# ===============================================================================
def check_r415_for_1_table():
    found_an_issue = False

    for G.DATABASE_NUM in range(len(A.KNOWN_DB)):
        if A.KNOWN_DB[G.DATABASE_NUM].database_base == G.TABLE_STRUCTURE.database_base_upper:
            break

    if A.KNOWN_DB[G.DATABASE_NUM].isa_base_db:
        pattern = re.compile('MULTISET', re.IGNORECASE)
        if pattern.search(G.TABLE_STRUCTURE.sql_stmt_txt):

            found_an_issue = check_r415_if_table_on_exception_list(pattern)

        elif G.VERBOSE:
            indent_debug('Good         : The BASE table {0}.{1} is a SET table.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper))

    elif G.VERBOSE:
        indent_debug('Notice       : {0}.{1} is not a BASE table so we do not check for Set/Multiset.'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper))

    return found_an_issue


# ===============================================================================
def check_r415():
    G.RULE_ID = 'r415'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if G.RULES_ENGINE_TYPE != 'TERADATA_DDL':
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_findings = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        if check_r415_for_1_table():
            num_findings += 1

    if num_findings > 1:
        indent_info('Notice       : Found {0} BASE tables that should not be Multiset.'.format(num_findings))
    elif num_findings == 1:
        indent_info('Notice       : Found {0} BASE table that should not be Multiset.'.format(num_findings))
    elif G.VERBOSE:
        indent_debug('Good         : Found no BASE tables that were Multiset without approval.')
