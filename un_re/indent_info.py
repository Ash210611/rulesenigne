import un_re.global_shared_variables as G


# ===============================================================================
def indent_info(message):
    """
        This function prints the message with a 15-space prefix
        """

    G.LOGGER.info((' ' * 15) + message)
