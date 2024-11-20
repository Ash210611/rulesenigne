import un_re.global_shared_variables as G


# ===============================================================================
def populate_workspace_tokens():
    """
    This function will split the G.WORKSPACE variable into tokens.

    These tokens are used by the get_rule_exceptions function, when it
    checks whether a rule is disabled for a project.  The project will
    be part of the path to the WORKSPACE.
    """

    G.WORKSPACE_TOKENS = G.WORKSPACE.split('/')

# if G.VERBOSE:
# 	G.LOGGER.debug ('The following tokens are found in the WORKSPACE variable')
# 	for token in G.WORKSPACE_TOKENS:
# 		G.LOGGER.debug ((' ' * 15) + token)
