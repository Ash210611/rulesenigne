# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent import indent
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r412_for_1_stmt():
    found_issue = False
    found_exception = False
    line = ''  # To satisfy pylint

    for line in G.OTHER_STATEMENT.sql_stmt_txt.split('\n'):
        if re.search(r'SELECT.*\*', line, re.IGNORECASE):
            if not re.search('COUNT', line, re.IGNORECASE):
                if re.search('MVC_INSERT_HIST', G.OTHER_STATEMENT.input_filename, re.IGNORECASE):
                    found_exception = True
                    break

                found_issue = True
                break

    if found_issue:
        G.LOGGER.info('')

        report_adjustable_finding(
            object_type_nm='FILE',
            object_nm=G.OTHER_STATEMENT.input_filename,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='Best practice is violated to Insert with Select *',
            adjusted_message=f'Accepting Insert with Select * in ruleset {G.OTHER_STATEMENT.ruleset}.',
            class_object=G.OTHER_STATEMENT)

        indent('Please do not use this syntax:')
        G.LOGGER.info(line)
        G.LOGGER.info('')
        indent('Please use a named column list instead.')

    elif found_exception:
        G.LOGGER.info('')
        indent('Notice:  This command does not use best practice to Insert with Select *')
        indent('         That will be allowed because the filename starts with MVC_INSERT_HIST')
        indent('         Filename: {0}'.format(G.OTHER_STATEMENT.input_filename.replace(G.WORKSPACE, '$WORKSPACE')))
        indent('         Stmt num: {0}'.format(G.OTHER_STATEMENT.sql_stmt_num))
        for line in G.OTHER_STATEMENT.sql_stmt_txt.split('\n'):
            G.LOGGER.info(line)
            if re.search(r'SELECT.*\*', line, re.IGNORECASE):
                G.LOGGER.info('...')
                break
        G.LOGGER.info('')

    elif G.VERBOSE:
        indent('Good         : File {0}, Stmt {1} Insert statement uses a named column list.'.format(
            G.OTHER_STATEMENT.input_filename.replace(G.WORKSPACE + '/', ''),
            G.OTHER_STATEMENT.sql_stmt_num))

    return found_issue


# ===============================================================================
def check_r412():
    """
    Search Insert statements for Select-Star.
    There may be more than 1 space between Select and Star
    Do not lump Select Count(*) with Select-Star
    """

    G.RULE_ID = 'r412'

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
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_findings = 0
    for G.OTHER_STATEMENT in G.OTHER_STATEMENTS:

        if G.OTHER_STATEMENT.command_type != "INSERT":
            return 0

        if check_r412_for_1_stmt():
            num_findings += 1

    if num_findings == 0:
        if G.VERBOSE:
            indent('Good         : No INSERT statements are selecting wildcards unexpectedly.')

    return 0
