# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_for_old_business_terms(string_source, string, string_parts, this_object_name):
    """
    Table and Column names should replace old business terms with new ones.

    To handle the case where the new business term contains the old
    business term, it is only matched if the string does not match the
    new business term.

    For example, BRNCH_CD should be replaced by ELGBTY_BRNCH_CD
    But since the new term contains the old term, we make sure the input
    string does not already match the new term.

    TODO: In the long run, the list of business terms should be read from a
    Postgres table.

    This function only reports if there actually are problems.  A lot of
    rules will also report if there are no problems, and for this function,
    it is excessively verbose to report if there are no problems.
    """

    business_term = None
    # Pylint recommends to initialize that.  Probably in case
    # the lists of old and new business terms is empty.

    found_old_business_term = False

    for business_term in G.BUSINESS_TERM_LIST:

        if string.upper() == business_term.new_term_txt.upper():
            # See doc string above for explanation of this
            # conditional. No need to check further.
            break

        if business_term.old_term_txt.find(r'_') > -1:
            # Then use it as a regular expression
            if re.search(rf'{business_term.old_term_txt}', string, re.IGNORECASE):
                found_old_business_term = True
                break

        else:
            patternstr = "^(.*[_])?{0}([_].*)?$".format(business_term.old_term_txt)
            compiled_p = re.compile(patternstr, re.IGNORECASE)
            if compiled_p.search(string):
                found_old_business_term = True
                break

    if found_old_business_term:

        if string_source == 'Column name':
            if string_parts[0].upper() == 'SRC':
                if G.VERBOSE:
                    indent_debug('Notice-{0}  : Passing {1} in SRC column {2}'.format(
                        G.RULE_ID,
                        business_term.old_term_txt,
                        this_object_name))
                    return False

        report_adjustable_finding(
            object_type_nm=string_source.upper(),
            object_nm=this_object_name,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='For {0}, {1}, replace old business term, {2}, with {3}.'.format(
                string_source.lower(),
                string,
                business_term.old_term_txt,
                business_term.new_term_txt),
            adjusted_message=
            'In {0} {1}, accepting old business term {2} in ruleset {3}.'.format(
                string_source.lower(),
                string,
                business_term.old_term_txt,
                G.TABLE_STRUCTURE.ruleset),
            class_object=G.TABLE_STRUCTURE)

    return found_old_business_term
