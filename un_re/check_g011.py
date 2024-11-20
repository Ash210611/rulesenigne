# pylint: disable=C0209           	# Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.check_r217 import check_r217_for_1_column
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_g011_for_1_column() -> bool:
    '''
    This is only checked for columns with more than 1 token.

    For example, for a column named EIN, is that SNAKE_CASE, or an
    abbreviation? It is impossible to say without knowing what an EIN
    actually is, so we have to skip it.
    '''

    found_an_issue = False

    if len(G.COLUMN_ELEMENT.column_name_tokens) == 1:
        # That cannot be an issue
        return found_an_issue  # return False

    if G.COLUMN_ELEMENT.naming_method != G.TABLE_STRUCTURE.naming_method:
        if check_r217_for_1_column(G.COLUMN_ELEMENT.name_upper):
            return False  # This column has a classword exception
        # Like TBLNM. The classword is NM, so it has more than
        # 1 token, but it does not use the SMASHED naming method.

        found_an_issue = True

        report_firm_finding(
            object_type_nm='COLUMN',
            object_nm='{0}.{1}'.format(
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_ELEMENT.name_upper),
            severity=G.RULES[G.RULE_ID].severity,
            message='Column {0}.{1} is using {2} inconsistently.'.format(
                G.TABLE_STRUCTURE.table_name_orig,
                G.COLUMN_ELEMENT.name_orig,
                G.COLUMN_ELEMENT.naming_method),
            class_object=G.TABLE_STRUCTURE)

    if G.COLUMN_ELEMENT.naming_method == 'MixedCase':
        if G.COLUMN_ELEMENT.column_name_tokens[0][0].islower():
            report_adjustable_finding(
                object_type_nm='COLUMN',
                object_nm=G.COLUMN_ELEMENT.name_upper,
                normal_severity=G.RULES[G.RULE_ID].severity,
                normal_message='MixedCase naming should start with a capital letter in {0} {1}.'.format(
                    'COLUMN',
                    G.COLUMN_ELEMENT.name_orig),
                adjusted_message='Accepting inconsistent case in ruleset {0}'.format(
                    G.INPUT_FILES[G.TABLE_STRUCTURE.get_filenum(G.INPUT_FILES)].ruleset),
                class_object=G.TABLE_STRUCTURE)

    return found_an_issue


# ===============================================================================
def check_g011_for_1_table() -> bool:
    found_an_issue = False

    if G.TABLE_STRUCTURE.ruleset == 'LANDINGZONE':
        # Landing zone columns want to conform to the source instead of
        # CCW, so we can't really check this rule g001 for Landing
        # Zone tables.
        return False  # Is not an issue.

    if G.TABLE_STRUCTURE.naming_method == '':
        found_an_issue = True

        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='No naming method was recognized for table {0}.'.format(
                G.TABLE_STRUCTURE.table_name_orig),
            class_object=G.TABLE_STRUCTURE)

    for G.COLUMN_ELEMENT in G.TABLE_STRUCTURE.column_elements:
        if check_g011_for_1_column():
            found_an_issue = True

    # if not found_an_issue and G.VERBOSE:
    # 	indent_debug ('Good         : A database context is found for table {0}.'.format (
    # 		G.TABLE_STRUCTURE.table_name_orig))

    return found_an_issue


# ===============================================================================
def check_g011() -> None:
    """
    A table name and the names of columns in that table must use a
    consistent naming method.

    The valid naming methods are 'SNAKE_CASE' and 'MixedCase'.

    This must be checked separately from reading the DDL statement, because
    reporting a finding needs attributes that are not available immediately,
    like the ruleset.
    """

    G.RULE_ID = 'g011'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))
    num_findings = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        if check_g011_for_1_table():
            num_findings += 1

    if num_findings > 1:
        indent_info('Notice       : Found {0} tables with an inconsistent naming method.'.format(num_findings))
    elif num_findings == 1:
        indent_info('Notice       : Found {0} table with an inconsistent naming method.'.format(num_findings))
    elif G.VERBOSE:
        indent_debug('Good         : All tables are using a consistent naming method.')

    return
