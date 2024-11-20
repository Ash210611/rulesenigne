import un_re.global_shared_variables as G


# ===============================================================================
def indent_debug(message):
    G.LOGGER.debug((' ' * 15) + message)
