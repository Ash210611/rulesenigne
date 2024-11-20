# pylint: disable=C0209           	# Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r005_for_1_index_1_tablespace():
    '''
    Check that each index is created in a tablespace for indexes.
    '''

    has_issue = False

    this_object_nm = '{0}.{1}'.format(
        G.INDEX_OBJ.database_base_upper,
        G.INDEX_OBJ.index_name_upper)

    if re.search('INDEX', G.INDEX_OBJ.tablespaces[0], re.IGNORECASE):
        indent_info('Good         : {0} will be in tablespace {1}'.format(
            this_object_nm,
            G.INDEX_OBJ.tablespaces[0]))

    elif re.search('DATA', G.INDEX_OBJ.tablespaces[0], re.IGNORECASE):
        has_issue = True

        report_adjustable_finding(
            object_type_nm='TABLESPACE',
            object_nm=this_object_nm,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='Index {0} will be in tablespace {1}.'.format(
                this_object_nm,
                G.INDEX_OBJ.tablespaces[0]),
            adjusted_message='Accepting index {0} in tablespace {1} for ruleset {2} .'.format(
                this_object_nm,
                G.INDEX_OBJ.tablespaces[0],
                G.INDEX_OBJ.ruleset),
            class_object=G.INDEX_OBJ)

        indent_info('Filenum, name: {0},{1}'.format(
            G.INDEX_OBJ.sql_stmt_obj.input_file.filenum + 1,
            G.INDEX_OBJ.sql_stmt_obj.input_file.input_filename.replace(
                G.WORKSPACE, '$WORKSPACE')))

        indent_info('Stmt Num     : {0}'.format(
            G.INDEX_OBJ.sql_stmt_obj.sql_stmt_num))

    elif G.VERBOSE:
        indent_info('Notice       : Unknown if {0} should be in tablespace {1}'.format(
            this_object_nm,
            G.INDEX_OBJ.tablespaces[0]))

    return has_issue


# ===============================================================================
def check_r005_for_1_table_1_tablespace():
    has_issue = False

    this_object_nm = '{0}.{1}'.format(
        G.TABLE_STRUCTURE.database_base_upper,
        G.TABLE_STRUCTURE.table_name_upper)

    if re.search('DATA', G.TABLE_STRUCTURE.tablespaces[0], re.IGNORECASE):
        indent_info('Good         : {0} will be in tablespace {1}'.format(
            this_object_nm,
            G.TABLE_STRUCTURE.tablespaces[0]))

    elif re.search('INDEX', G.TABLE_STRUCTURE.tablespaces[0], re.IGNORECASE):
        has_issue = True

        report_adjustable_finding(
            object_type_nm='TABLESPACE',
            object_nm=this_object_nm,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='Table {0} will be in tablespace {1}.'.format(
                this_object_nm,
                G.TABLE_STRUCTURE.tablespaces[0]),
            adjusted_message='Accepting table {0} in tablespace {1} for ruleset {2} .'.format(
                this_object_nm,
                G.TABLE_STRUCTURE.tablespaces[0],
                G.TABLE_STRUCTURE.ruleset),
            class_object=G.TABLE_STRUCTURE)

        indent_info('Filenum, name: {0},{1}'.format(
            G.TABLE_STRUCTURE.sql_stmt_obj.input_file.filenum + 1,
            G.TABLE_STRUCTURE.sql_stmt_obj.input_file.filename.replace(
                G.WORKSPACE, '$WORKSPACE')))

        indent_info('Stmt Num     : {0}'.format(
            G.TABLE_STRUCTURE.sql_stmt_obj.sql_stmt_num))

    elif G.VERBOSE:
        indent_info('Notice       : Unknown if {0} should be in tablespace {1}'.format(
            this_object_nm,
            G.TABLE_STRUCTURE.tablespaces[0]))

    return has_issue


# ===============================================================================
def check_r005_for_1_index_n_tablespaces():
    has_issue = False

    this_object_nm = '{0}.{1}'.format(
        G.INDEX_OBJ.database_base_upper,
        G.INDEX_OBJ.index_name_upper)

    for tablespace_name in list(set(G.INDEX_OBJ.tablespaces)):
        if re.search('INDEX', tablespace_name, re.IGNORECASE):
            indent_info('Good         : Part of {0} will be in tablespace {1}'.format(
                this_object_nm,
                tablespace_name))

        elif re.search('DATA', tablespace_name, re.IGNORECASE):
            has_issue = True

            report_adjustable_finding(
                object_type_nm='TABLESPACE',
                object_nm=this_object_nm,
                normal_severity=G.RULES[G.RULE_ID].severity,
                normal_message='Part of index {0} will be in tablespace {1}.'.format(
                    this_object_nm,
                    tablespace_name),
                adjusted_message='Accepting index {0} in tablespace {1} for ruleset {2} .'.format(
                    this_object_nm,
                    tablespace_name,
                    G.INDEX_OBJ.ruleset),
                class_object=G.INDEX_OBJ)

            indent_info('Filenum, name: {0},{1}'.format(
                G.INDEX_OBJ.sql_stmt_obj.input_file.filenum + 1,
                G.INDEX_OBJ.sql_stmt_obj.input_file.filename.replace(
                    G.WORKSPACE, '$WORKSPACE')))

            indent_info('Stmt Num     : {0}'.format(
                G.INDEX_OBJ.sql_stmt_obj.sql_stmt_num))

        elif G.VERBOSE:
            indent_info('Notice       : Unknown if {0} should be in tablespace {1}'.format(
                this_object_nm,
                tablespace_name))

    return has_issue


# ===============================================================================
def check_r005_for_1_table_n_tablespaces():
    has_issue = False

    this_object_nm = '{0}.{1}'.format(
        G.TABLE_STRUCTURE.database_base_upper,
        G.TABLE_STRUCTURE.table_name_upper)

    for tablespace_name in list(set(G.TABLE_STRUCTURE.tablespaces)):
        # Use list-set to deduplicate the tablespace names
        if re.search('DATA', tablespace_name, re.IGNORECASE):
            indent_info('Good         : Part of {0} will be in tablespace {1}'.format(
                this_object_nm,
                tablespace_name))

        elif re.search('INDEX', tablespace_name, re.IGNORECASE):
            has_issue = True

            report_adjustable_finding(
                object_type_nm='TABLESPACE',
                object_nm=this_object_nm,
                normal_severity=G.RULES[G.RULE_ID].severity,
                normal_message='Part of table {0} will be in tablespace {1}.'.format(
                    this_object_nm,
                    G.TABLE_STRUCTURE.tablespaces[0]),
                adjusted_message='Accepting table {0} in tablespace {1} for ruleset {2} .'.format(
                    this_object_nm,
                    tablespace_name,
                    G.TABLE_STRUCTURE.ruleset),
                class_object=G.TABLE_STRUCTURE)

            indent_info('Filenum, name: {0},{1}'.format(
                G.TABLE_STRUCTURE.sql_stmt_obj.input_file.filenum + 1,
                G.TABLE_STRUCTURE.sql_stmt_obj.input_file.filename.replace(
                    G.WORKSPACE, '$WORKSPACE')))

            indent_info('Stmt Num     : {0}'.format(
                G.TABLE_STRUCTURE.sql_stmt_obj.sql_stmt_num))

        elif G.VERBOSE:
            indent_info('Notice       : Unknown if {0} should be in tablespace {1}'.format(
                this_object_nm,
                tablespace_name))

    return has_issue


# ===============================================================================
def check_r005_has_an_index_issue():
    has_issue = False

    this_object_nm = '{0}.{1}'.format(
        G.INDEX_OBJ.database_base_upper,
        G.INDEX_OBJ.index_name_upper)

    num_tablespaces = len(G.INDEX_OBJ.tablespaces)

    if num_tablespaces > 1:
        has_issue = check_r005_for_1_index_n_tablespaces()

    elif num_tablespaces == 1:
        has_issue = check_r005_for_1_index_1_tablespace()

    else:
        indent_info('Notice       : {0} has no specified tablespace name.'.format(
            this_object_nm))

    return has_issue


# ===============================================================================
def check_r005_has_a_table_issue():
    has_issue = False

    this_object_nm = '{0}.{1}'.format(
        G.TABLE_STRUCTURE.database_base_upper,
        G.TABLE_STRUCTURE.table_name_upper)

    num_tablespaces = len(G.TABLE_STRUCTURE.tablespaces)

    if num_tablespaces > 1:
        has_issue = check_r005_for_1_table_n_tablespaces()

    elif num_tablespaces == 1:
        has_issue = check_r005_for_1_table_1_tablespace()

    else:
        indent_info('Notice       : {0} has no specified tablespace name.'.format(
            this_object_nm))

    return has_issue


# ===============================================================================
def check_r005_indexes():
    if len(G.INDEX_OBJS) == 0:
        if G.VERBOSE:
            indent_info('Notice       : No CREATE INDEX commands were found')
        return

    num_issues_found = 0
    num_indexes_checked = 0

    for G.INDEX_OBJ in G.INDEX_OBJS:
        if G.INDEX_OBJ.sql_stmt_obj.command_type not in (
                'CREATE INDEX',
                'ALTER TABLE CONSTRAINT'):
            continue

        num_indexes_checked += 1

        if check_r005_has_an_index_issue():
            num_issues_found += 1

    if num_issues_found > 0:
        indent_info('Notice       : Checked {0} indexes, found {1} tablespace-location issues'.format(
            num_indexes_checked,
            num_issues_found))
        return

    # else
    if G.VERBOSE:
        if num_issues_found == 0:
            indent_info('Good         : No indexes have tablespace-location issues.')


# ===============================================================================
def check_r005_tables():
    if len(G.TABLE_STRUCTURES) == 0:
        if G.VERBOSE:
            indent_info('Notice       : No CREATE TABLE commands were found')
        return

    num_issues_found = 0
    num_tables_checked = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:
        if G.TABLE_STRUCTURE.sql_stmt_obj.command_type != 'CREATE TABLE':
            # An Alter Table command might add a column, and leave
            # the tablespace untouched.  We will need a actual
            # test case to prove what the developers need to check
            # that or not.
            continue

        num_tables_checked += 1

        if check_r005_has_a_table_issue():
            num_issues_found += 1

    if num_issues_found > 0:
        indent_info('Notice       : Checked {0} tables, found {1} tablespace-location issues'.format(
            num_tables_checked,
            num_issues_found))
        return

    # else
    if G.VERBOSE:
        if num_issues_found == 0:
            indent_info('Good         : No tables have tablespace-location issues.')


# ===============================================================================
def check_r005():
    '''
    Return 0 if no issues are found
    Return 1 if any issues are found.
    '''

    G.RULE_ID = 'r005'
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    check_r005_tables()
    check_r005_indexes()
