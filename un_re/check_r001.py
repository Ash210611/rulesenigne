# pylint: disable=C0209                 # Don't require formatted strings

import un_re.global_shared_variables as G

from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r001():
    '''
    Return 0 if all Grant statements pass.
    Return 1 if any issues are found.
    '''

    num_issues_found = 0
    G.RULE_ID = 'r001'

    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    if len(G.GRANT_STATEMENTS) == 0:
        indent_info('Notice       : No GRANT commands were found.')
        return 0

    for grant_statement in G.GRANT_STATEMENTS:
        if grant_statement.granted_permission == 'SYSDBA':
            num_issues_found += 1

            report_firm_finding(
                object_type_nm='COMMAND',
                object_nm='GRANT',
                severity=G.RULES[G.RULE_ID].severity,
                message='Granting SYSDBA is not allowed',
                class_object=G.TABLE_STRUCTURE)

            indent_info('Filenum, name: {0},{1}'.format(
                grant_statement.input_file.filenum + 1,
                grant_statement.input_file.input_filename.replace(
                    G.WORKSPACE, '$WORKSPACE')))
            indent_info(f'Stmt Num     : {grant_statement.sql_stmt_num}')
            G.LOGGER.info('')

    if num_issues_found == 0:
        indent_info('Good         : All GRANT commands are allowed.')
        return 0

    # else:
    indent_info('Notice       : Disallowed {0} of {1} GRANT statements'.format(
        num_issues_found,
        len(G.GRANT_STATEMENTS)))

    return 1
