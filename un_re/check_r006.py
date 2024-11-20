# pylint: disable=C0209                 # Don't require formatted strings

import un_re.global_shared_variables as G

from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r006():
    '''
    Disallow physical DBA commands.
    And issue a Warning about UNKNOWN commands.

    UNKNOWN commands are often the result of a procedure building-up a SQL
    statement in a character string, and issuing an EXECUTE IMMEDIATE
    command to send it to the database.  The character string only has a
    value at runtime, so the Rules Engine does not know what the text of the
    character string actually is ahead of time.
    '''

    num_issues_found = 0
    G.RULE_ID = 'r006'

    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    for sql_stmt_obj in G.SQL_STATEMENT_OBJS:
        if sql_stmt_obj.antlr_status != 'SUCCEEDED':
            continue

        stmt_is_ok = True
        if sql_stmt_obj.command_type == 'UNKNOWN':
            stmt_is_ok = False
            stmt_severity = 'WARNING'
            stmt_message = 'Command Type is UNKNOWN'
        else:
            stmt_severity = G.RULES[G.RULE_ID].severity
            stmt_message = 'Command type {0} is not allowed'.format(
                sql_stmt_obj.command_type)

        if sql_stmt_obj.command_type in (
                'ALTER USER',
                'CREATE TABLESPACE',
                'CREATE USER',
                'DROP DATABASE',
                'DROP DISKGROUP',
                'DROP FLASHBACK ARCHIVE',
                'DROP PMEM FILESTORE',
                'DROP ROLLBACK SEGMENT',
                'DROP TABLESPACE',
                'DROP TABLESPACE SET',
                'DROP USER',
                'FLASHBACK DATABASE',
                'FLASHBACK TABLE',
                'NOAUDIT',
                'PURGE'):
            stmt_is_ok = False
            num_issues_found += 1

        if not stmt_is_ok:
            report_firm_finding(
                object_type_nm='COMMAND TYPE',
                object_nm=sql_stmt_obj.command_type,
                severity=stmt_severity,
                message=stmt_message,
                class_object=sql_stmt_obj)

            indent_info('Filenum, name: {0},{1}'.format(
                sql_stmt_obj.input_file.filenum + 1,
                sql_stmt_obj.input_file.input_filename.replace(
                    G.WORKSPACE, '$WORKSPACE')))
            indent_info(f'Stmt Num     : {sql_stmt_obj.sql_stmt_num}')
            G.LOGGER.info('')

    if num_issues_found == 0:
        indent_info('Good         : All SQL commands are allowed.')
        return 0

    # else:
    indent_info('Notice       : Disallowed {0} of {1} SQL statements'.format(
        num_issues_found,
        len(G.SQL_STATEMENT_OBJS)))

    return 1
