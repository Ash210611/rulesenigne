# pylint: disable=C0209		# Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug


# ===============================================================================
def check_r217_for_1_column(name_upper):
    '''
    Note that this function cannot use the binary search, because some
    exceptions may contain column parts themselves.
    '''

    found_an_exception = False

    word = ''  # In case the exception list is empty

    for word in G.PHYSICAL_CLASSWORD_EXCEPTION_LIST:
        patternstr = f'^(.*[_])?{word}([_].*)?$'
        compiled_pattern = re.compile(patternstr, re.IGNORECASE)
        if compiled_pattern.search(name_upper):
            found_an_exception = True
            break

    if found_an_exception and G.VERBOSE:
        indent_debug('Notice-r217  : {0}.{1}.{2} uses classword exception {3}.  '.format(
            G.TABLE_STRUCTURE.database_base_upper,
            G.TABLE_STRUCTURE.table_name_upper,
            name_upper,
            word) + 'Will skip r216 for this column.')

    return found_an_exception


# ===============================================================================
def check_r217_for_1_table():
    '''
    Rule 216 calls this function directly.

    We don't check rules 217 directly, rather 216 uses this function
    to check if the classword for this column has an exception.
    '''

    G.COLUMN_ELEMENTS = G.TABLE_STRUCTURE.column_elements

    found_an_exception = False

    for G.COLUMN_ELEMENT in G.COLUMN_ELEMENTS:
        # -----------------------------------------------------------------------
        # Check the rule

        if check_for_rule_exception(G.RULE_ID,
                                    G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper,
                                    G.COLUMN_ELEMENT.name_upper):
            continue

        if check_r217_for_1_column(G.COLUMN_ELEMENT.name_upper):
            found_an_exception = True

    return found_an_exception


# ===============================================================================
def check_r217():
    """
    Columns names may use a classword exception.
    If they do, r216 will be skipped.

    """

    G.RULE_ID = 'r217'

    # -----------------------------------------------------------------------
    # Check prerequisites

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:
        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            continue

        check_r217_for_1_table()
