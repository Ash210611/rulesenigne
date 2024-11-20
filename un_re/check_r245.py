# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_bad_characters import check_for_bad_characters
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_r245():
    '''
    Check table names for bad characters
    '''

    G.RULE_ID = 'r245'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    total_found_with_bad_chars = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        msg = check_for_bad_characters(G.TABLE_STRUCTURE.table_name_upper)

        if msg != '':
            total_found_with_bad_chars += 1

            report_adjustable_finding(
                object_type_nm='TABLE NAME',
                object_nm=G.TABLE_STRUCTURE.table_name_upper,
                normal_severity=G.RULES[G.RULE_ID].severity,
                normal_message='{0}.{1}: {2}'.format(
                    G.TABLE_STRUCTURE.database_base_upper,
                    G.TABLE_STRUCTURE.table_name_upper,
                    msg),
                adjusted_message=
                'Accepting {0}.{1} with bad characters in ruleset {2}.'.format(
                    G.TABLE_STRUCTURE.database_base_upper,
                    G.TABLE_STRUCTURE.table_name_upper,
                    G.TABLE_STRUCTURE.ruleset),
                class_object=G.TABLE_STRUCTURE)
        else:
            if G.VERBOSE:
                indent_debug('Good         : No bad characters found in table name {0}.{1}.'.format(
                    G.TABLE_STRUCTURE.database_base_orig,
                    G.TABLE_STRUCTURE.table_name_orig))

    if G.VERBOSE:
        if total_found_with_bad_chars == 0:
            indent_debug('Good         : No table names found with bad characters.')

    return 0
