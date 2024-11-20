# pylint: disable=C0209           		# Don't require formtted strings
# pylint: disable=R0912				# Too many branches
# pylint: disable=R0913				# Too many arguments

import os
import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding
from un_re.split_value_from_line import split_value_from_line


# ===============================================================================
# 	Suppose we have this test case:
#		SELECT 	<fields>
#		from 	GRPR_EBM_LAST_SVC_DT_PROF
#		WHERE  	rpt_end_dt = (
#			select cast(rpt_end_dt as date format 'YYYY-MM-DD')
#			from	VT_V2V_RPT_END_DT_GRPR)
#		;
#
#	We need a way to recognize the tables are joined in the subquery.
#
#	The Antlr output is:
#	...
#	Found relation source        : Some_DB.GRPR_EBM_LAST_SVC_DT_PROFSomething
#	  relationPrimary alias      :   null
#	Parsed relationPrimary       : Some_DB.GRPR_EBM_LAST_SVC_DT_PROFSomething
#	primaryExpression.cast       : rpt_end_dt
#	projected_expression.alt1    : cast(rpt_end_dtasdateformat'YYYY-MM-DD')
#
#	Projected_expression         : cast(rpt_end_dtasdateformat'YYYY-MM-DD')
#	Found relation source        : VT_V2V_RPT_END_DT_GRPR
#	  relationPrimary alias      :   null
#	Parsed relationPrimary       : VT_V2V_RPT_END_DT_GRPR
#	primaryExpression.query      : selectcast(rpt_end_dtasdateformat'YYYY-MM-DD')fromVT_V2V_RPT_END_DT_GRPR
#	  left primaryExpression     : rpt_end_dt
#	  comparison_operator        : =
#	  right primaryExpression    : (selectcast(rpt_end_dtasdateformat'YYYY-MM-DD')fromVT_V2V_RPT_END_DT_GRPR)
#	boolean_comparison.left      : rpt_end_dt=(selectcast(rpt_end_dtasdateformat'YYYY-MM-DD')fromVT_V2V_RPT_END_DT_GRPR)
#	boolean_comparison.right     : null
#	Found where clause           : rpt_end_dt=(selectcast(rpt_end_dtasdateformat'YYYY-MM-DD')fromVT_V2V_RPT_END_DT_GRPR)
#
#	So the algorithm will be:
#		once we find a relation source, start looking for a subquery.
#		save the name of that relation source
#		if we find a primaryExpression.query with that relation source, count it.
#		stop looking for a subquery if another kind of join is found.
#
#	It is tempting to rezero the subquery count if the FROM clause has not
#	been reached yet, because a cartesian product would fail in the 
#	projection list.   Unfortunately, it would require us to track the
#	recursion level, and our Antlr grammer does not currently know how to 
#	do that.
#
# ===============================================================================
def count_sources():
    '''
    Notice that this depends on scanning the both the tokens and the actions
    from the Antlr log filename.   In other words, it needs to scan
    the Antlr full log filename.
    '''

    num_sources = 0
    num_joins = 0
    num_exists = 0
    num_in_expressions = 0
    num_load_ctl_refs = 0
    num_unions = 0
    num_subquery_joins = 0

    look_for_subquery_joins = False
    source_name = ''

    for line in G.ANTLR_LOG_CONTENTS.split('\n'):
        if look_for_subquery_joins:
            if re.search('primaryExpression.query      :', line):
                query = split_value_from_line(line)
                if re.search(source_name, query):
                    num_subquery_joins += 1
                    look_for_subquery_joins = False

        if re.search('Found relation source        :', line):
            num_sources += 1
            look_for_subquery_joins = True
            source_name = split_value_from_line(line)

            if re.search('CCW_INFA_CTL_HIST', line, re.IGNORECASE):
                num_load_ctl_refs += 1
            elif re.search('CCW_LOAD_CTL_STATS', line, re.IGNORECASE):
                num_load_ctl_refs += 1
            elif re.search('CCW_LOAD_CTL', line, re.IGNORECASE):
                num_load_ctl_refs += 1
            elif re.search('vt_load_ctl_key', line, re.IGNORECASE):
                num_load_ctl_refs += 1

        elif re.search("'JOIN'", line, re.IGNORECASE):
            num_joins += 1
            look_for_subquery_joins = False

        elif re.search('Found WITH clause            :', line):
            # It is too hard to analyze statements with WITH clauses.
            return -1, -1, -1, -1, -1, -1, -1

        elif re.search("'EXISTS'", line, re.IGNORECASE):
            num_exists += 1
            look_for_subquery_joins = False
        elif re.search("Finished IN list v1 for      : ", line, re.IGNORECASE):
            num_in_expressions += 1
            look_for_subquery_joins = False
        elif re.search("'UNION'", line, re.IGNORECASE):
            num_unions += 1
            look_for_subquery_joins = False

    return (num_sources, num_joins, num_exists, num_in_expressions,
            num_load_ctl_refs, num_unions, num_subquery_joins)


# ===============================================================================
def report_excess_relational_warning(
        num_sources, num_joins, num_exists, num_in_expressions,
        num_load_ctl_refs, num_unions, num_subquery_joins):
    this_object_nm = G.SQL_STATEMENT_OBJ.input_filename.replace(G.WORKSPACE + '/', '') + \
                     ', Stmt: {0}'.format(
                         G.SQL_STATEMENT_OBJ.sql_stmt_num + 1)

    report_adjustable_finding(
        object_type_nm='SQL',
        object_nm=this_object_nm,
        normal_severity=G.RULES[G.RULE_ID].severity,
        normal_message='Excess relational sources found.',
        adjusted_message='Accepting excess relational sources in ruleset {0}'.format(
            G.SQL_STATEMENT_OBJ.ruleset),
        class_object=G.SQL_STATEMENT_OBJ)

    for preview_line in G.SQL_STATEMENT_OBJ.get_a_little_context():
        indent_info(preview_line)

    if num_joins > 0:
        indent('Num joins found              : {0}'.format(num_joins))
    if num_exists > 0:
        indent('Num exists found             : {0}'.format(num_exists))
    if num_in_expressions > 0:
        indent('Num in expressions found     : {0}'.format(num_in_expressions))
    if num_load_ctl_refs > 0:
        indent('Num load-ctl references found: {0}'.format(num_load_ctl_refs))
    if num_unions > 0:
        indent('Num unions found             : {0}'.format(num_unions))
    if num_subquery_joins > 0:
        indent('Num subquery joins found     : {0}'.format(num_subquery_joins))

    indent('Num relational sources found : {0}'.format(num_sources))
    G.LOGGER.warning('')
    for line in G.ANTLR_LOG_CONTENTS.split('\n'):
        if re.search('Found relation source        :', line):
            indent((' ' * 9) + line.strip())
    G.LOGGER.info('')


# ===============================================================================
def report_num_relational_sources(
        num_sources, num_joins, num_exists, num_in_expressions,
        num_load_ctl_refs, num_unions, num_subquery_joins):
    if num_joins > 0:
        indent_debug('Notice       : Num joins found              : {0}.'.format(num_joins))
    if num_exists > 0:
        indent_debug('Notice       : Num exists found             : {0}.'.format(num_exists))
    if num_in_expressions > 0:
        indent_debug('Notice       : Num in expressions found     : {0}.'.format(num_in_expressions))
    if num_load_ctl_refs > 0:
        indent_debug('Notice       : Num load-ctl references found: {0}.'.format(num_load_ctl_refs))
    if num_unions > 0:
        indent_debug('Notice       : Num unions found             : {0}.'.format(num_unions))
    if num_subquery_joins > 0:
        indent_debug('Notice       : Num subquery joins found     : {0}.'.format(num_subquery_joins))

    indent_debug('Notice       : Num relational sources found : {0}.'.format(num_sources))
    G.LOGGER.debug('')
    for line in G.ANTLR_LOG_CONTENTS.split('\n'):
        if re.search('Found relation source        :', line):
            G.LOGGER.debug((' ' * 30) + line.strip())
    indent_debug('Good         : No excess relational sources found.')


# ===============================================================================
def dreml_check_num_sources():
    found_an_issue = False

    antlr_full_log_filename = G.SQL_STATEMENT_OBJ.antlr_log_filename.replace('.antlr.re.log', '.antlr_full.re.log')

    G.ANTLR_LOG_CONTENTS = get_file_contents(antlr_full_log_filename)

    (num_sources, num_joins, num_exists, num_in_expressions,
     num_load_ctl_refs, num_unions, num_subquery_joins) = count_sources()

    if num_sources == -1:
        if G.VERBOSE:
            indent_debug('Notice       : Not checking excess relational sources for this stmt.')
    else:
        if num_sources > num_joins + num_exists + num_in_expressions + \
                num_load_ctl_refs + num_unions + num_subquery_joins + 1:

            report_excess_relational_warning(
                num_sources, num_joins, num_exists, num_in_expressions,
                num_load_ctl_refs, num_unions, num_subquery_joins)

            found_an_issue = True

        elif G.VERBOSE:

            report_num_relational_sources(
                num_sources, num_joins, num_exists, num_in_expressions,
                num_load_ctl_refs, num_unions, num_subquery_joins)

    return found_an_issue


# ===============================================================================
def check_r509():
    G.RULE_ID = 'r509'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_stmts_w_findings = 0

    for G.SQL_STATEMENT_OBJ in G.SQL_STATEMENT_OBJS:

        if G.SQL_STATEMENT_OBJ.command_type in (
                'CREATE TABLE',
                'DEFAULT DATABASE'):
            continue

        indent_info('File, Stmt # : {0}, {1}.'.format(
            os.path.basename(G.SQL_STATEMENT_OBJ.input_filename),
            G.SQL_STATEMENT_OBJ.sql_stmt_num + 1))

        if dreml_check_num_sources():
            num_stmts_w_findings += 1

    num_stmts = len(G.SQL_STATEMENT_OBJS)
    if num_stmts_w_findings > 1:
        indent_info('Notice       : {0} statements of {1} have excess relational sources.'.format(
            num_stmts_w_findings,
            num_stmts))

    elif num_stmts_w_findings == 1:
        indent_info('Notice       : 1 statement of {0} has an excess relational source'.format(
            num_stmts))

    elif G.VERBOSE:
        indent('Good         : No statements have excess relational sources.')
