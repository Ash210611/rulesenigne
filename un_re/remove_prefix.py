#
#
# This function is inspired from this source:
#	https://stackoverflow.com/questions/16891340/remove-a-prefix-from-a-string
# ==============================================================================
def remove_prefix(input_text, prefix):
    """
    Remove a prefix from an input string, if the prefix is found.
    """

    if input_text.startswith(prefix):
        return input_text[len(prefix):]

    return input_text
