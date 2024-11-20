import un_re.global_shared_variables as G


# ===============================================================================
def indent_error(message):
    G.LOGGER.error((' ' * 15) + message)
