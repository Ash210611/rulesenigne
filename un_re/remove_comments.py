# pylint: disable=C0301		# Don't limit line length
#
# The functions in this module are useful for removing multi-line comment
# blocks of the form /*...*/
#
# These functions are adapted from this source:
#	https://stackoverflow.com/questions/844681/python-regex-question-stripping-multi-line-comments-but-maintaining-a-line-brea
#
# The one thing I changed is the re.compile search string.
# I changed the original search string:
#	r'(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?'
# to
#	r'(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*)($)?'
#
# because SQL comments can start with --
#
# Note that this is not perfect.  For example it does not handle pathologically
# nested comment blocks. But is is pretty good.
#
# I would like to study this more at the website Jeremy recommended:
# 	regex101.com
#
# Testing on that website indicate this should work better:
#	(--.*$|\/\*[\s\S]*?\*\/)
# ==============================================================================

import re
import sqlparse  # type: ignore

import un_re.global_shared_variables as G

# ==============================================================================
COMMENT_RE = re.compile(
    r'(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*)($)?',
    re.DOTALL | re.MULTILINE)

DASHDASH_RE = re.compile(r'--.*$', re.MULTILINE)


def comment_replacer(match):
    start, mid, end = match.group(1, 2, 3)
    if mid is None:
        # single line comment
        return ''

    if start is not None or end is not None:
        # multi line comment at start or end of a line
        return ''

    if '\n' in mid:
        # multi line comment with line break
        return '\n'

    # multi line comment without line break
    return ' '


# ===============================================================================
def remove_comments(sql):
    # Remove block comments
    sql = COMMENT_RE.sub(comment_replacer, sql)

    # Remove one-line comments
    # sql = DASHDASH_RE.sub (r'\n', sql)

    # 5/8/2019 Testing a new way to remove one-comments, adapted from:
    # https://stackoverflow.com/questions/5871791/howto-clean-comments-from-raw-sql-file

    try:
        new_sql = sqlparse.format(sql, strip_comments=True).strip()
    except RecursionError:
        G.LOGGER.info('Warning : Failed to remove comments from SQL')
        G.LOGGER.info('Warning : Exceeded recursion limit in the sqlparse module.')
        G.LOGGER.info(f'SQL: {sql}')
        return sql

    return new_sql


# ===============================================================================
def remove_comments_alt(sql):
    '''
    10/2/2020 Try to adapt this alternative:
    https://stackoverflow.com/questions/2319019/using-regex-to-remove-comments-from-source-files

    This version does work.   If a line only contains a comment, this version
    will leave a blank line.  The sqlparse version above will remove that
    line, resulting in more concise output
    '''

    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|--[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)

    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.

        if match.group(2) is not None:
            return ""  # so we will return empty to remove the comment

        # else, we will return the 1st group
        return match.group(1)  # captured quoted-string

    return regex.sub(_replacer, sql)
