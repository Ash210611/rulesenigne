# pylint: disable=C0209           # Don't require formtted strings

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.binary_search import binary_search
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def check_articles(string_type, string, string_parts, rule_id, ruleset):
    """
    Table and Column names should not contain an article.

    R258 calls this function for table names.
    Rsomething will call this function for column names.

    In the long run, the list of articles should be read from a Postgres
    table.
    """
    G.RULE_ID = rule_id

    found_article = False

    if check_for_rule_exception(G.RULE_ID):
        return found_article

    string_part = 'UNKNOWN'  # Provide default value for pylint

    for string_part in string_parts:
        comparison_part = C.Article(string_part.upper())
        found_article = binary_search(G.ARTICLE_LIST, comparison_part)

        if found_article:
            break

    if string_part == 'UNKNOWN':
        # Then there were no string parts.
        G.LOGGER.error('No string parts found.')

    if found_article:

        if string_type == 'Column name':
            if string_parts[0].upper() == 'SRC':
                if G.VERBOSE:
                    indent_debug('Notice-{0}  : Passing article {1} in SRC column {2}'.format(
                        G.RULE_ID,
                        string_part,
                        string))

                return False

        report_adjustable_finding(
            object_type_nm=string_type.upper(),
            object_nm=string,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message=f'{string_type}, {string}, contains an article, {string_part}.',
            adjusted_message='Accepting an article for {0}, {1}, in ruleset {2}'.format(
                string_type,
                string,
                ruleset),
            class_object=G.TABLE_STRUCTURE)

    # Let the caller decide how to report the finding
    # elif G.VERBOSE:
    #	G.LOGGER.debug ((' ' * 15) + 'Good         : The {0} does not contain an article.'.format (
    #	 	string_type.lower () ))

    return found_article
