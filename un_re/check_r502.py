# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.indent_info import indent_info
from un_re.indent_warning import indent_warning
from un_re.print_msg import report_firm_finding


# ===============================================================================
def is_ok_to_add_right_column(right_column):
    """
    Only add this right column to the collection if it is table column, not
    a system column or a constant
    """

    if right_column == 'CURRENT_DATE':  # Will we find more examples?
        return False

    if re.search("'.*'", right_column):  # Something in single quotes
        return False

    return True


# ===============================================================================
def report_right_reference(expression_value):
    this_object_nm = G.SQL_STATEMENT_OBJ.input_filename.replace(G.WORKSPACE + '/', '') + \
                     f', Stmt: {G.SQL_STATEMENT_OBJ.sql_stmt_num + 1}'

    report_firm_finding(
        object_type_nm='SQL',
        object_nm=this_object_nm,
        severity=G.RULES[G.RULE_ID].severity,
        message='A left-join right-column issue was found.',
        class_object=G.SQL_STATEMENT_OBJ)

    indent_warning(f'Sql Stmt Num : {G.SQL_STATEMENT_OBJ.sql_stmt_num + 1}')
    indent_warning(f'Column used  : {expression_value}')


# ===============================================================================
def dreml_check_l_join_r_col(antlr_log_contents):  # pylint: disable=too-many-branches
    '''
    The way this works is:
    - Read the Antlr log filename, one line at a time.
    - After you see a line that indicates Left Outer Join, then
    -   start making note of the right column names, and
    -   stop making note when that join is finished being checked.
    - After that, check left and right primary Expressions.
    - Raise a warning if the right column name is used in those.

    To reduce work and skip duplicates, break after the first issue is
    found.
    '''

    found_an_issue = False
    collect_right_sides = False
    right_relation_sources = []
    right_relation_aliases = []

    for line in antlr_log_contents.split('\n'):
        if not re.search(': ', line):
            continue

        if re.search('Found join type              : LEFT OUTER', line):
            collect_right_sides = True
        elif re.search('Parsed relational join       :', line):
            # We are finished parsing that relational join
            collect_right_sides = False
        elif re.search('Found join type              : RIGHT OUTER', line):
            collect_right_sides = False
            right_relation_sources = []
            right_relation_aliases = []

        if collect_right_sides:
            if re.search('Found relation source        :', line):

                relation_source = line.split(':')[1]
                relation_source = relation_source.strip()

                right_relation_sources.append(relation_source)

            # G.LOGGER.debug ('Found right column: {0}'.format (right_column))
            elif re.search('  relationPrimary alias      :', line):
                relation_alias = line.split(':')[1]
                relation_alias = relation_alias.strip()

                right_relation_aliases.append(relation_alias)

        elif re.search('  ON search condition        :', line):
            pass

        elif re.search('ROW_NUMBER', line):
            pass

        else:
            if re.search('  left primaryExpression     :', line) or \
                    re.search('  right primaryExpression    :', line):

                found_a_right_reference = False
                expression_value = line.split(':')[1]
                expression_value = expression_value.strip()

                for right_relation_source in right_relation_sources:
                    if re.search(right_relation_source, expression_value, re.IGNORECASE):
                        found_a_right_reference = True

                for right_relation_alias in right_relation_aliases:
                    if re.search(r'{0}\.'.format(right_relation_alias), expression_value, re.IGNORECASE):
                        found_a_right_reference = True

                if found_a_right_reference:
                    report_right_reference(expression_value)
                    found_an_issue = True
                    break
                # To reduce work and skip duplicates,
                # bail after only 1 issue is found.

    if G.VERBOSE:
        if not found_an_issue:
            G.LOGGER.debug((' ' * 15) + 'Good         : Found no misused left-join right-columns.')

    return found_an_issue


# ===============================================================================
def check_r502():
    G.RULE_ID = 'r502'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_stmts_w_findings = 0

    for G.SQL_STATEMENT_OBJ in G.SQL_STATEMENT_OBJS:

        G.ANTLR_LOG_FILENAME = G.SQL_STATEMENT_OBJ.antlr_log_filename

        G.ANTLR_LOG_CONTENTS = get_file_contents(G.ANTLR_LOG_FILENAME)

        # print (G.SQL_STATEMENT_OBJ)

        if dreml_check_l_join_r_col(G.ANTLR_LOG_CONTENTS):
            num_stmts_w_findings += 1

    if num_stmts_w_findings > 1:
        indent_info('Notice       : {0} statements have a left-join right-column issue.'.format(
            num_stmts_w_findings))

    elif num_stmts_w_findings == 1:
        indent_info('Notice       : 1 statement has a left-join right-column issue.')

    elif G.VERBOSE:
        indent('Good         : No statements have a left-join right-column issue.')
