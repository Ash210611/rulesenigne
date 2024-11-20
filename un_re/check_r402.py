# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r402_for_1_table():
    found = False

    for option in G.TABLE_STRUCTURE.regulated_options:
        this_object_nm = f'{G.TABLE_STRUCTURE.table_name_upper}: {option}'
        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=this_object_nm,
            severity=G.RULES[G.RULE_ID].severity,
            message='{0}.{1} has unexpected content: {2}'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                option),
            class_object=G.TABLE_STRUCTURE)

        found = True

    if not found and G.VERBOSE:
        indent_info('Good         : Table {0}.{1} has no unexpected content.'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper))

    return found


# ===============================================================================
def check_r402():
    """
    Check for any unexpected content.
    For example, in a Create Table command, it is unexpected to find
    NO PRIMARY INDEX.

    This function is imposed on the whole DDL file.

    The NO CHECK constraints are checked by later after the input file is
    split apart.
    """

    G.RULE_ID = 'r402'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    if G.RULES_ENGINE_TYPE != 'TERADATA_DDL':
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_findings = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            return 0

        if check_r402_for_1_table():
            num_findings += 1

    if num_findings > 1:
        indent_info('Notice       : {0} tables have some unexpected content.'.format(num_findings))

    elif num_findings == 1:
        indent_info('Notice       : {0} table has some unexpected content.'.format(num_findings))

    elif G.VERBOSE:
        indent_info('Good         : No tables had any unexpected content.')

    return 0
