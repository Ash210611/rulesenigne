# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent import indent
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r403_for_1_table():
    is_a_nopi_table = False
    found_an_issue = False

    for regulated_option in G.TABLE_STRUCTURE.regulated_options:
        if regulated_option == 'NO PRIMARY INDEX':
            is_a_nopi_table = True

    if not is_a_nopi_table:
        pattern = re.compile(r'PRIMARY\s*INDEX', re.IGNORECASE)

        if not pattern.search(G.TABLE_STRUCTURE.sql_stmt_txt):
            is_a_nopi_table = True

    if is_a_nopi_table:
        if G.TABLE_STRUCTURE.database_base_upper == 'VOLATILE':

            indent('Notice       : Allowing NOPI for {0}.{1}.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper))
        else:
            found_an_issue = True

            report_firm_finding(
                object_type_nm='TABLE',
                object_nm=G.TABLE_STRUCTURE.table_name_upper,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0}.{1} has no PRIMARY INDEX clause.'.format(
                    G.TABLE_STRUCTURE.database_base_upper,
                    G.TABLE_STRUCTURE.table_name_upper),
                class_object=G.TABLE_STRUCTURE)

    elif G.VERBOSE:
        indent('Good         : {0}.{1} has a primary index clause.'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper))

    return found_an_issue


# ===============================================================================
def check_r403():
    """
    Check that a Primary Index clause exists
    """

    G.RULE_ID = 'r403'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if G.RULES_ENGINE_TYPE not in (
            'TERADATA_DDL',
            'TERADATA_DML'):
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    total_num_findings = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            return 0

        if G.TABLE_STRUCTURE.command_type not in (
                'CREATE TABLE',
                'CREATE TABLE AS SELECT'):
            # Do not check this for ALTER TABLE commands
            continue

        if check_r403_for_1_table():
            total_num_findings += 1

    if total_num_findings == 0:
        if G.VERBOSE:
            indent('Good         : All tables have a primary index clause that need one.')

    return 0
