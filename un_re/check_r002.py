# pylint: disable=C0209           	# Don't require formtted strings

import un_re.global_shared_variables as G

from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r002_for_one_table():
    if not G.TABLE_STRUCTURE.primary_key_is_specified:
        this_object_nm = '{0}.{1}'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper)

        report_adjustable_finding(
            object_type_nm='TABLE',
            object_nm=this_object_nm,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='A primary key is not specified for Table {0}'.format(
                this_object_nm),
            adjusted_message='Accepting table {0} without PK in ruleset {1}.'.format(
                this_object_nm,
                G.TABLE_STRUCTURE.ruleset),
            class_object=G.TABLE_STRUCTURE)

        # indent_info ('Filenum, name: {0},{1}'.format (
        # 		G.TABLE_STRUCTURE.sql_stmt_obj.input_file.filenum + 1,
        # 		G.TABLE_STRUCTURE.sql_stmt_obj.input_file.input_filename.replace (
        # 			G.WORKSPACE, '$WORKSPACE')))
        indent_info('Stmt Num     : {0}'.format(
            G.TABLE_STRUCTURE.sql_stmt_obj.sql_stmt_num))

        return 1

    if G.VERBOSE:
        indent_info('Good         : A primary key is specified for Table {0}.{1}'.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper))
    return 0


# ===============================================================================
def check_r002():
    '''
    Return 0 if all tables have a primary key.
    Return 1 if any issues are found.
    '''

    G.RULE_ID = 'r002'
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_issues_found = 0
    num_tables_checked = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:
        if G.TABLE_STRUCTURE.sql_stmt_obj.command_type == 'CREATE TABLE AS SELECT':
            num_tables_checked += 1
            if len(G.TABLE_STRUCTURE.column_elements) == 0:
                continue
            # You can't check for a primary key if the
            # columns are not specified.
            # A different rule will check CTAS statements
            # without columns

        elif G.TABLE_STRUCTURE.sql_stmt_obj.command_type == 'CREATE TABLE':
            num_tables_checked += 1
            if G.TABLE_STRUCTURE.database_base_upper == 'LIVE':
                indent_info('Not checking primary key for Live table: {0}'.format(
                    G.TABLE_STRUCTURE.table_name_upper))
                continue
            # LIVE tables cannot have a primary key

        else:
            continue

        # Check if a subsequent Alter Table command creates a
        # primary key on this table.
        for ts in G.TABLE_STRUCTURES:
            if ts.command_type == 'ALTER TABLE CONSTRAINT' and \
                    ts.database_base_upper == G.TABLE_STRUCTURE.database_base_upper and \
                    ts.table_name_upper == G.TABLE_STRUCTURE.table_name_upper and \
                    ts.primary_key_is_specified:
                G.TABLE_STRUCTURE.primary_key_is_specified = ts.primary_key_is_specified

        # An Alter Table command might add a column, and leave
        # the primary key untouched.  We will need a actual
        # test case to prove what the developers need or not.

        num_issues_found += check_r002_for_one_table()

    if num_issues_found > 0:
        indent_info('Notice       : A primary key is not specified for {0} of {1} tables'.format(
            num_issues_found,
            num_tables_checked))
        return 1

    # else
    if G.VERBOSE:
        if num_tables_checked == 0:
            indent_info('Notice       : No CREATE TABLE commands were found.')
        elif num_issues_found == 0:
            indent_info('Good         : A primary key is specified for all tables where appropriate.')
    return 0
