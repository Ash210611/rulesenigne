# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r401_for_1_table():
    num_findings = 0

    num_matches_needed = len(G.EXPECTED_CONTENT)

    cleaned_sql_statement = G.TABLE_STRUCTURE.sql_stmt_txt.replace('\n', ' ')

    num_matches_found = 0
    for z_line in G.EXPECTED_CONTENT:
        z_line = z_line.strip()
        if re.search(z_line, cleaned_sql_statement, re.IGNORECASE):
            num_matches_found += 1

    if num_matches_needed != num_matches_found:
        num_findings += 1

        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='Table {0}.{1} is missing some expected content.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper),
            class_object=G.TABLE_STRUCTURE)

        # Display the content that was expected
        G.LOGGER.error((' ' * 30) + 'This is the content that was expected.')
        for z_line in G.EXPECTED_CONTENT:
            z_line = z_line.strip()
            if not re.search(z_line, G.TABLE_STRUCTURE.sql_stmt_txt, re.IGNORECASE):
                z_line = z_line.replace(r'\s+', ' ')
                indent((' ' * 15) + z_line)

    elif G.VERBOSE:
        indent_debug('Good         : {0}.{1} includes all expected content.'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper))

    return num_findings


# ===============================================================================
def check_r401():
    """
    Check for all expected content.
    For example, every Create Table command is expected to include a
    Primary Index.

    Some DDL will say NO PRIMARY INDEX, and that does contain the phrase
    PRIMARY INDEX, which is allowed for VOLATILE tables. That combination of
    conditions is checked by the nearby rule 403.
    """

    G.RULE_ID = 'r401'

    # -----------------------------------------------------------------------
    # Check prerequisites

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    if G.VERBOSE:
        num_regexes = len(G.EXPECTED_CONTENT)

        if num_regexes == 1:
            indent_info((' ' * 15) + 'Checking that %d regular expression is found.' % num_regexes)
        else:
            indent_info((' ' * 15) + 'Checking that %d regular expressions are found.' % num_regexes)

    total_num_findings = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        if G.TABLE_STRUCTURE.command_type not in (
                'CREATE TABLE',
                'CREATE TABLE AS SELECT'):
            # Do not check this for ALTER TABLE commands

            continue

        num_findings = check_r401_for_1_table()
        total_num_findings += num_findings

    if total_num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All tables include all expected content')

    else:
        if total_num_findings == 1:
            indent_info('Notice       : {0} table missed some expected content'.format(total_num_findings))
        else:
            indent_info('Notice       : {0} tables missed some expected content'.format(total_num_findings))

    return 0
