# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding

SET_TYPE_IS_UNKNOWN = 0
SET_TYPE_IS_SET = 1
SET_TYPE_IS_MULTISET = 2

UNQ_TYPE_IS_UNIQUE = 3
UNQ_TYPE_IS_NON_UNIQUE = 4


# ===============================================================================
def dreml_check_multiset_loop():
    """
    This function will loop through each line of the antlr_log_contents
    and set the flags depending on what it finds.
    """

    table_set_type = SET_TYPE_IS_UNKNOWN
    uniqueness_type = UNQ_TYPE_IS_NON_UNIQUE  # by default

    for line in G.ANTLR_LOG_CONTENTS.split('\n'):
        if re.search('MULTISET', line, re.IGNORECASE):
            table_set_type = SET_TYPE_IS_MULTISET
            break

        if re.search('  Found table set type       : ', line, re.IGNORECASE):
            line_value = line.split(':')[1]
            line_value = line_value.strip()
            line_value = line_value.upper()

            if line_value == 'SET':
                table_set_type = SET_TYPE_IS_SET
            elif line_value == 'MULTISET':
                table_set_type = SET_TYPE_IS_MULTISET

        elif re.search('Found constraint type        : ', line, re.IGNORECASE) or \
                re.search('Found data type constraint   : ', line, re.IGNORECASE) or \
                re.search("  uniqueness                 : ", line, re.IGNORECASE):

            line_value = line.split(':')[1]
            line_value = line_value.strip()
            line_value = line_value.upper()

            if re.search('UNIQUE', line_value):
                uniqueness_type = UNQ_TYPE_IS_UNIQUE
            elif re.search('PRIMARY KEY', line_value):
                uniqueness_type = UNQ_TYPE_IS_UNIQUE

    return table_set_type, uniqueness_type


# ===============================================================================
def dreml_check_multiset_decide(table_set_type, uniqueness_type):
    """
    This function will check the flags, and decide what
    findings to report.

    Return True if there is an issue, else return False if there is no issue.
    """

    if table_set_type == SET_TYPE_IS_UNKNOWN:
        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='Table {0} set type is not set explicitly.'.format(
                G.TABLE_STRUCTURE.table_name_upper),
            class_object=G.TABLE_STRUCTURE)
        G.LOGGER.info((' ' * 15) + 'In that case, it depends on the session mode, either ANSI or Teradata.')
        G.LOGGER.info((' ' * 15) + 'That setting is not known and not trusted.')
        G.LOGGER.info((' ' * 15) + 'Please specify SET or MULTISET explicitly.')
        return True

    if table_set_type == SET_TYPE_IS_SET and uniqueness_type == UNQ_TYPE_IS_UNIQUE:
        if G.VERBOSE:
            indent_debug('Good         : The SET volatile table {0} is created with uniqueness.'.format(
                G.TABLE_STRUCTURE.table_name_upper))
        return False

    if table_set_type == SET_TYPE_IS_SET and uniqueness_type == UNQ_TYPE_IS_NON_UNIQUE:
        report_firm_finding(
            object_type_nm='TABLE',
            object_nm=G.TABLE_STRUCTURE.table_name_upper,
            severity=G.RULES[G.RULE_ID].severity,
            message='The SET volatile table is created without a unique index.',
            class_object=G.TABLE_STRUCTURE)
        return True

    if table_set_type == SET_TYPE_IS_MULTISET:
        if G.VERBOSE:
            indent_debug('Good         : ETL table {0} is explicitly MULTISET.'.format(
                G.TABLE_STRUCTURE.table_name_upper))
        return False

    return True


# ===============================================================================
def dreml_check_multiset():
    """
    This function checks that Volatile tables are created
    with the Multiset attribute.

    The Rule will be
    table_set_type	Primary_Index	Acceptable
    SET		UPI		Yes
    SET		NUPI		NO
    MULTISET	UPI		Yes
    MULTISET	NUPI		Yes

    By default, if a table does not say UNIQUE somewhere, then it is
    non-unique.

    If the table does not specify SET or MULTISET, then the table_set_type
    depends on the session mode.

    See TD 15.10 SQL Data Definition Language, p29 for that default.

    All create-table commands checked by the DML Rules Engine must either
    be Volatile or be an ERR database.
    """

    (table_set_type, uniqueness_type) = \
        dreml_check_multiset_loop()

    return dreml_check_multiset_decide(table_set_type, uniqueness_type)


# ===============================================================================
def check_r503():
    G.RULE_ID = 'r503'

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
                'CREATE TABLE',
                'CREATE TABLE AS SELECT'):
            continue

        G.ANTLR_LOG_FILENAME = G.TABLE_STRUCTURE.antlr_log_filename

        G.ANTLR_LOG_CONTENTS = get_file_contents(G.ANTLR_LOG_FILENAME)

        if dreml_check_multiset():
            num_tables_w_an_issue += 1

    if num_tables_w_an_issue > 1:
        indent_info('Notice       : {0} ETL Create Table statements is setting the type ambiguously.'.format(
            num_tables_w_an_issue))

    elif num_tables_w_an_issue == 1:
        indent_info('Notice       : 1 ETL Create Table statement is setting the type ambiguously.')

    elif G.VERBOSE:
        indent('Good         : No ETL Create Table statements have an issue with set type.')
