import re

import un_re.global_shared_variables as G


# ===============================================================================
def check_for_bad_characters(string):
    """
    A data model table name, column name, or definition, should not contain
    bad characters (Ex. 2 underscores together, tab, ~, ^, etc).

    A valid string source is one of these:
        'table name'
        'column name'
        'table comment'
        'column comment'

    An appropriate source name is either the table name or column name.

    The string is the source name or comment string to check.

    Note: 10/7/2019: I am commenting out the expressions to check for
    single or double quotes, because unlike Teradata for CCW, Hive can
    use either single or double quotes.  And the Antlr syntax check
    will catch unbalanced quotes as a syntax error.
    """

    # pylint: disable=R0911			# too-many-return-statements

    if re.search(r'__', string, re.MULTILINE):
        return '2 consecutive underscores'

    if G.RULES_ENGINE_TYPE != 'HIVE_DDL_RE':
        # Hive allows comments to be delimited with either single or
        # double quotes, so the database will check this better
        # than I can
        if re.search(r"'", string, re.MULTILINE):
            string = string.replace("''''", '')
            string = string.replace("''", '')
            num_quote_1 = string.count("'")
            if num_quote_1 > 0:
                return 'a single-quote character'

        if re.search(r'"', string, re.MULTILINE):
            return 'a double-quote character'

    if re.search('\\t', string, re.MULTILINE):
        return 'a tab character'

    if re.search(r'~', string, re.MULTILINE):
        return 'a tilde character'

    if re.search(r'\^', string, re.MULTILINE):
        return 'a caret character'

    return ''
