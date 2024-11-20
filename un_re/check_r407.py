# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent import indent
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r407_for_1_table():
    found_an_issue = False
    num_foreign_keys_found = 0

    for foreign_key_clause in G.TABLE_STRUCTURE.foreign_key_clauses:

        num_foreign_keys_found += 1
        if not re.search(r'NOCHECKOPTION', foreign_key_clause):
            # Antlr removes the whitespace from the FK clause

            found_an_issue = True

            report_firm_finding(
                object_type_nm='TABLE',
                object_nm=G.TABLE_STRUCTURE.table_name_upper,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0}.{1} foreign key constraint must specify the NO CHECK OPTION.'.format(
                    G.TABLE_STRUCTURE.database_base_upper,
                    G.TABLE_STRUCTURE.table_name_upper),
                class_object=G.TABLE_STRUCTURE)

            indent_info((' ' * 15) + 'FK Constraint: {0}'.format(foreign_key_clause))

    if not found_an_issue:
        if G.VERBOSE:
            if num_foreign_keys_found > 0:
                indent('Good         : {0}.{1} num foreign keys accepted: {2}.'.format(
                    G.TABLE_STRUCTURE.database_base_upper,
                    G.TABLE_STRUCTURE.table_name_upper,
                    num_foreign_keys_found))
            else:
                indent('Good         : {0}.{1} had no foreign keys to check.'.format(
                    G.TABLE_STRUCTURE.database_base_upper,
                    G.TABLE_STRUCTURE.table_name_upper))

    return found_an_issue


# ===============================================================================
def check_r407():
    """
    If the command specifies a foreign key, then it must also specify
    the NO CHECK OPTION
    """

    G.RULE_ID = 'r407'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    total_num_findings = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        if check_r407_for_1_table():
            total_num_findings += 1

    if total_num_findings > 1:
        indent_info(
            'Notice       : {0} tables have a foreign key without the no-check option.'.format(total_num_findings))

    elif total_num_findings == 1:
        indent_info(
            'Notice       : {0} table has a foreign key without the no-check option.'.format(total_num_findings))

    elif G.VERBOSE:
        indent('Good         : No tables have foreign keys without the no-check option.')

    return 0
