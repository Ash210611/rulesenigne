# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_old_business_terms import check_for_old_business_terms
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info


# ===============================================================================
def check_r253_for_1_table():
    this_object_name = f'{G.TABLE_STRUCTURE.database_base_upper}.' + \
                       f'{G.TABLE_STRUCTURE.table_name_upper}'

    return check_for_old_business_terms(
        'Table name',
        G.TABLE_STRUCTURE.table_name_upper,
        G.TABLE_STRUCTURE.table_name_tokens,
        this_object_name)


# ===============================================================================
def check_r253():
    """
    This function checks that table names do not contain obsolete business
    terms.
    """

    G.RULE_ID = 'r253'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        if G.TABLE_STRUCTURE.table_name_tokens[0].upper() in ('W', 'TEMP', 'TMP'):
            # Skip this rule for work tables.
            indent_debug('Notice-{0}  : Skipping {0} for a Work table.'.format(
                G.RULE_ID))
            continue

        if check_r253_for_1_table():
            num_findings += 1

    if num_findings > 1:
        indent_info(f'Notice       : Found {num_findings} table names with obsolete business terms.')
    elif num_findings == 1:
        indent_info('Notice       : Found 1 table name with an obsolete business term.')
    elif G.VERBOSE:
        indent_debug('Good         : Found no table names with obsolete business terms.')

    return 0
