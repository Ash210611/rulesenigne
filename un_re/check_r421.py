import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r421():
    G.RULE_ID = 'r421'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0

    for G.OTHER_STATEMENT in G.OTHER_STATEMENTS:

        if G.OTHER_STATEMENT.command_type != "GRANT":
            continue

        num_findings += 1

        report_firm_finding(
            object_type_nm='FILE',
            object_nm=G.OTHER_STATEMENT.input_filename,
            severity=G.RULES[G.RULE_ID].severity,
            message='A GRANT permission command was found.',
            class_object=G.OTHER_STATEMENT)

        for line in G.OTHER_STATEMENT.sql_stmt_txt.split('\n'):
            indent_info(line)

    if num_findings > 1:
        indent_info(f'Notice       : {num_findings} GRANT commands were found.')

    elif num_findings == 1:
        indent_info(f'Notice       : {num_findings} GRANT command was found.')

# elif G.VERBOSE:
#        indent ('Good         : No GRANT commands were found.')
# These are rare, and there is little need to be verbose
# about passing this rule.
