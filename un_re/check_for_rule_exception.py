# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.print_msg import print_msg


# ===============================================================================
def lookup_class_object():
    '''
    Lookup the filename that the Table Structure is referenced in.

    But not every object is a table, so beware this might not work for everything!
    '''

    if G.TABLE_STRUCTURE is not None:
        for input_file in G.INPUT_FILES:
            if input_file.input_filename == G.TABLE_STRUCTURE.input_filename:
                return input_file

    return None


# ===============================================================================
def exception_matches_rule(exc_rule_id, rule_id):
    if exc_rule_id == 'ALL':
        return True

    if exc_rule_id == rule_id:
        return True

    return False


# ===============================================================================
def exception_matches_project(exc_project_name, project_name):
    # if G.RULE_ID == 'r403':
    #	print ('')
    #	print (f'  exc_project_name={exc_project_name}')
    #	print (f'      project_name={project_name}')

    if exc_project_name == 'ALL':
        # if G.RULE_ID == 'r403':
        #	print ('Returning True for ALL projects')
        return True

    if re.search(exc_project_name, project_name, re.IGNORECASE):
        # if G.RULE_ID == 'r403':
        #	print ('Project matches.  Will check the table name')
        return True

    for token in G.WORKSPACE_TOKENS:
        if token.upper() == exc_project_name.upper():
            # if G.RULE_ID == 'r403':
            #	print ('Returning true for matching a workspace token')
            return True

    # if G.RULE_ID == 'r403':
    #	print ('Project does not match')
    return False


# ===============================================================================
def exception_matches_table(exc_table_name, table_name):
    if exc_table_name == 'ALL':
        return True

    if exc_table_name.find('%') > -1:
        string_to_match = exc_table_name.replace('%', '.*')

        if re.search(string_to_match, table_name, re.IGNORECASE):
            return True

    elif exc_table_name.upper() == table_name.upper():
        return True

    return False


# ===============================================================================
def exception_matches_column(exc_column_name, column_name):
    if exc_column_name == 'ALL':
        return True

    if exc_column_name.upper() == column_name.upper():
        return True

    if exc_column_name.find('%') > -1:
        string_to_match = exc_column_name.replace('%', '.*?')

        if re.search(string_to_match, column_name):
            return True

    return False


# ===============================================================================
def report_exception_found(rule_id, exc_project_name, exc_table_name, exc_column_name):
    print_msg('Notice-{0}  : Granted exception for Rule {0}, Project {1}, Table {2}, Column {3}.'.format(
        rule_id, exc_project_name, exc_table_name, exc_column_name))


# ===============================================================================
def check_for_rule_exception(
        rule_id,
        project_name='ALL',
        table_name='ALL',
        column_name='ALL'):
    '''
    To turn a rule off for all Projects, all Tables or all Columns, then
        remove that rule from the rules.lst file

    DDL exceptions can be definied using 4 parameters - the rule id, the
        project, the table and the column.

    Parameters are not (yet) partially matched with a wildcard.  You can
        match all values of a parameter by specifying ALL, or you can
        match a specific value explicitly.

    We will loop through the list of exceptions records, and break out of
        the loop on the first exception that matches all 4 parameters.
    '''

    for rules_exception_record in G.RULES_EXCEPTION:
        if rules_exception_record.is_expired:
            continue

        (exc_rule_id, exc_project_name, exc_table_name, exc_column_name) = rules_exception_record.pk.split('|')

        if not exception_matches_rule(exc_rule_id, rule_id):
            continue

        # if G.RULE_ID == 'r403':
        # 	print ('')
        # 	print ('Rule ID {0} passes. Will check project name {1}.'.format (exc_rule_id, exc_project_name))
        if not exception_matches_project(exc_project_name, project_name):
            continue

        # if G.RULE_ID == 'r403':
        #	print ('  Project Name {0} passes. Will check table name.{1}'.format (exc_project_name, exc_table_name))
        if not exception_matches_table(exc_table_name, table_name):
            continue

        # if G.RULE_ID == 'r403':
        #	print ('    Table name {0} passes. Will check column name {1}.'.format (exc_table_name, exc_column_name))
        if not exception_matches_column(exc_column_name, column_name):
            continue

        # if it reaches here, it has matched all 4 parameters.

        # if G.RULE_ID == 'r403':
        #	print ('      Column name {0} passes. Will report the exception.'.format (exc_column_name))
        report_exception_found(rule_id, exc_project_name, exc_table_name, exc_column_name)

        return True  # found_exception = True

    return False  # found_exception = False
