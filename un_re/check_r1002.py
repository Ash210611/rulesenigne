# import    sys

import re

import un_re.global_shared_vars as G

from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding

SET_TYPE_IS_UNKNOWN = 0
SET_TYPE_IS_SET = 1
SET_TYPE_IS_MULTISET = 2
UNQ_TYPE_IS_UNIQUE = 3
UNQ_TYPE_IS_NON_UNIQUE = 4
UNQ_TYPE_IS_NO_UNIQUE = 5
UNQ_TYPE_IS_UNKNOWN = 6
FALL_BACK_UNKNOWN = 7
FALL_BACK_YES = 8
FALL_BACK_NO = 9


# ===============================================================================
def check_r1002_multiset_decide(table_set_type, uniqueness_type, fallback_type):
    """
    This function will check the flags, and decide what
    findings to report.
    """

    replacevalue = False
    if fallback_type == FALL_BACK_UNKNOWN:
        report_firm_finding(
            object_type_nm='FILE',
            object_nm=G.TABLE_STRUCTURE.input_filename,
            severity=G.RULES[G.RULE_ID].severity,
            message='The table {0}.{1} is created with unknown fall back.'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper),
            class_object=G.TABLE_STRUCTURE)
        replacevalue = True

    elif (
            table_set_type == SET_TYPE_IS_SET or table_set_type == SET_TYPE_IS_MULTISET) and fallback_type == FALL_BACK_YES:
        # indent_info ('TABLE_STRUCTURE       : {0}'.format (G.TABLE_STRUCTURE))
        report_firm_finding(
            object_type_nm='FILE',
            object_nm=G.TABLE_STRUCTURE.input_filename,
            severity=G.RULES[G.RULE_ID].severity,
            message='The SET/MULTISET table {0}.{1} is created with fallback option,expected NO FALLBACK'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper),
            class_object=G.TABLE_STRUCTURE)
        replacevalue = True

    elif (
            table_set_type == SET_TYPE_IS_SET or table_set_type == SET_TYPE_IS_MULTISET) and fallback_type == FALL_BACK_NO:
        if G.VERBOSE:
            indent_info('*' * 100)
            indent_info('Good         : The SET/MULTISET table {0} is created with expected no fallback option'.format(
                G.TABLE_STRUCTURE.table_name_upper))
            indent_info('*' * 100)
        replacevalue = False
    return replacevalue


# ===============================================================================
def check_r1002_multiset_loop():
    """
    This function will loop through each line of the antlr_log_contents
    and set the flags depending on what it finds.
    """

    table_set_type = SET_TYPE_IS_UNKNOWN
    uniqueness_type = UNQ_TYPE_IS_UNKNOWN
    fallback_type = FALL_BACK_UNKNOWN
    # by default

    # indent_info ('sql_statement       : {0}'.format (G.TABLE_STRUCTURE.sql_statement))

    if re.search("MULTISET", G.TABLE_STRUCTURE.sql_statement, re.IGNORECASE):
        table_set_type = SET_TYPE_IS_MULTISET
    elif re.search("SET", G.TABLE_STRUCTURE.sql_statement, re.IGNORECASE):
        table_set_type = SET_TYPE_IS_SET

    if re.search("NO PRIMARY INDEX", G.TABLE_STRUCTURE.sql_statement, re.IGNORECASE):
        uniqueness_type = UNQ_TYPE_IS_NO_UNIQUE
    elif re.search("UNIQUE PRIMARY INDEX", G.TABLE_STRUCTURE.sql_statement, re.IGNORECASE):
        uniqueness_type = UNQ_TYPE_IS_UNIQUE
    elif re.search("PRIMARY INDEX", G.TABLE_STRUCTURE.sql_statement, re.IGNORECASE):
        uniqueness_type = UNQ_TYPE_IS_NON_UNIQUE

    if re.search("FALLBACK", G.TABLE_STRUCTURE.sql_statement, re.IGNORECASE):
        fallback_type = FALL_BACK_YES
    else:
        fallback_type = FALL_BACK_NO

    return (table_set_type, uniqueness_type, fallback_type)


# ===============================================================================
def check_r1002_multiset_UPI():
    """
    This function checks that Volatile tables are created
    with the Multiset attribute.

    The Rule will be
    table_set_type  Primary_Index   Acceptable
    MULTISET    UPI     NO
    MULTISET    NUPI        Yes

    By default, if a table does not say UNIQUE somewhere, then it is
    non-unique.

    If the table does not specify SET or MULTISET, then the table_set_type
    depends on the session mode.

    See TD 15.10 SQL Data Definition Language, p29 for that default.
    """

    # indent_info ('ANTLR LOG CONTENT       : {0}'.format (G.ANTLR_LOG_CONTENTS))

    if G.TABLE_STRUCTURE.command_type != 'CREATE TABLE' and \
            G.TABLE_STRUCTURE.command_type != 'CREATE TABLE AS SELECT':
        # print ('This is not a Create Table statement')
        return 0

    if re.search('VOLATILE', G.TABLE_STRUCTURE.sql_statement, re.IGNORECASE):
        indent_info('Table {0} is a Volatile table.'.format(
            G.TABLE_STRUCTURE.table_name_upper))
        return 0

    if not (re.search('MULTISET', G.TABLE_STRUCTURE.sql_statement, re.IGNORECASE) or re.search('SET',
                                                                                               G.TABLE_STRUCTURE.sql_statement,
                                                                                               re.IGNORECASE)):
        indent_info('Table {0} is not a SET or MULTISET table.'.format(
            G.TABLE_STRUCTURE.table_name_upper))
        return 0

    (table_set_type, uniqueness_type, fallback_type) = \
        check_r1002_multiset_loop()

    # indent_info ('Set Type and uniqueness       : {0} {1} {2}'.format (table_set_type,uniqueness_type,fallback_type))
    return check_r1002_multiset_decide(table_set_type, uniqueness_type, fallback_type)


# ===============================================================================
def check_r1002():
    G.RULE_ID = 'r1002'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    if G.RULES_ENGINE_TYPE != 'TERADATA_DDL':
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    G.LOGGER.info('=' * 100)

    num_findings = 0

    # indent_info ('TABLE STRUCTURES       : {0}'.format (G.TABLE_STRUCTURES))

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        # indent_info ('Starting Validation for TABLE NAME       : {0}'.format (G.TABLE_STRUCTURE.table_name_upper))

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            return 0

        if check_r1002_multiset_UPI():
            num_findings += 1

    if num_findings > 1:
        # indent_info ('*' * 120)
        indent_info('Notice       : {0} tables have some unexpected content.'.format(num_findings))
        indent_info('*' * 100)

    elif num_findings == 1:
        # print('*' * 120)
        indent_info('Notice       : {0} table has some unexpected content.'.format(num_findings))
        indent_info('*' * 100)

    elif G.VERBOSE:
        indent_info('*' * 100)
        indent_info('Good         : No tables had any unexpected content.')
        indent_info('*' * 100)

    G.LOGGER.info('=' * 100)
    return 0
