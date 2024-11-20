import re


# ===============================================================================
def remove_sqlplus_prompts(contents):
    '''
    Comment-out SQLPlus PROMPT commands, which cannot be automated.
    '''

    regex = r"(^PROMPT.*?$)"
    subst = r'/* \1 */'

    contents = re.sub(regex, subst, contents, 99, re.MULTILINE | re.IGNORECASE)

    return contents
