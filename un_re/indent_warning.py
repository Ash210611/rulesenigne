import un_re.global_shared_variables as G


# ===============================================================================
def indent_warning(message):
    G.LOGGER.warning((' ' * 15) + message)
