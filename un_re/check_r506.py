# pylint: disable=C0209           # Don't require formtted strings

import re
import sys

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def should_skip_this_line(line):
    # Skip looking on lines for relational sources.
    if re.search('Parsed relationPrimary       :', line):
        should_skip = True

    elif re.search('Parsed single_statement      :', line):
        should_skip = True

    elif re.search('primaryExpression.query      :', line):
        should_skip = True

    elif re.search('projected_expression.alt1    :', line):
        should_skip = True

    elif re.search('EXISTS', line, re.IGNORECASE):
        should_skip = True  # because there will be a subquery, and it will check that.

    elif re.search('SELECT', line, re.IGNORECASE):
        should_skip = True  # because ditto

    else:
        should_skip = False

    return should_skip


# ===============================================================================
def report_r506_finding(expression_value, relational_sources):
    report_adjustable_finding(
        object_type_nm='FILE',
        object_nm=G.SQL_STATEMENT_OBJ.input_filename,
        normal_severity=G.RULES[G.RULE_ID].severity,
        normal_message='Found inconsistent alias.',
        adjusted_message='Accepting inconsistent alias for ruleset {0}'.format(
            G.SQL_STATEMENT_OBJ.ruleset),
        class_object=G.SQL_STATEMENT_OBJ)

    indent_info('Stmt context :')
    for preview_line in G.SQL_STATEMENT_OBJ.get_a_little_context():
        indent_info(preview_line)

    for expr_source in relational_sources:
        search_string = r'\b{0}\b'.format(expr_source)
        if re.search(search_string, expression_value):
            indent_info(f"Expr'on value: {expression_value}")
            indent_info(f'Source       : {expr_source}')


# ===============================================================================
# noinspection PyUnusedLocal
def dreml_check_relational_alias():
    G.ANTLR_LOG_CONTENTS = get_file_contents(G.SQL_STATEMENT_OBJ.antlr_log_filename)

    relational_sources = []
    relational_aliases = []

    looking_for_alias = False
    look_for_inconsistent_alias = False
    found_one = False
    relational_source = ''
    relational_alias = ''

    for line in G.ANTLR_LOG_CONTENTS.split('\n'):
        if not re.search(': ', line):
            continue

        if re.search('Found relation source        :', line):
            relational_source = line.split(':')[1]
            relational_source = relational_source.strip()
            look_for_inconsistent_alias = True

            if looking_for_alias:
                # then the previous relation was not aliased.
                relational_alias = ''
            else:
                looking_for_alias = True

        elif re.search('  relationPrimary alias      :', line):
            if not looking_for_alias:
                # How can this happen??
                G.LOGGER.error('Found unexpected alias.')
                G.LOGGER.error(f'Line: {line}')
                sys.exit(33)

            if line.find('null') == -1:
                # If the alias is null, there is no alias.
                relational_alias = line.split(':')[1]
                relational_alias = relational_alias.strip()

                looking_for_alias = False
                relational_sources.append(relational_source)
                relational_aliases.append(relational_alias)

        elif look_for_inconsistent_alias:
            # Skip certain kinds of lines
            if should_skip_this_line(line):
                continue

            expression_value = line.split(':')[1]
            expression_value = expression_value.strip()

            for source in relational_sources:
                search_string = r'\b{0}\b'.format(source)
                if re.search(search_string, expression_value):
                    found_one = True

                    # Only report the finding once per
                    # statement, because it needs to be
                    # revised anyway.

                    report_r506_finding(expression_value,
                                        relational_sources)

                    return found_one  # Returning true

    return found_one  # would return False


# ===============================================================================
def check_r506():
    G.RULE_ID = 'r506'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_stmts_checked = 0
    num_stmts_w_findings = 0
    num_update_stmts = 0

    for G.SQL_STATEMENT_OBJ in G.SQL_STATEMENT_OBJS:

        if G.SQL_STATEMENT_OBJ.antlr_status != 'SUCCEEDED':
            continue

        num_stmts_checked += 1

        if G.SQL_STATEMENT_OBJ.command_type == 'UPDATE':
            num_update_stmts += 1
            continue

        if dreml_check_relational_alias():
            num_stmts_w_findings += 1

    if num_stmts_w_findings > 1:
        indent_info('Notice       : {0} statements of {1} have an inconsistent alias.'.format(
            num_stmts_w_findings,
            num_stmts_checked))

    elif num_stmts_w_findings == 1:
        indent_info('Notice       : 1 statement of {0} has an inconsistent alias.'.format(
            num_stmts_checked))

    elif G.VERBOSE:
        indent('Good         : No statements of {0} have an inconsistent alias.'.format(
            num_stmts_checked))

        if num_update_stmts > 1:
            indent_debug('Notice       : Skipped checking relational aliases for {0} UPDATE statements.'.format(
                num_update_stmts))
        elif num_update_stmts == 1:
            indent_debug('Notice       : Skipped checking relational aliases for an UPDATE statement.')
