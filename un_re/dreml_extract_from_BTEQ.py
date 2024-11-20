from un_re.dreml_extract_from_ksh import dreml_extract_from_ksh


# ===============================================================================
def dreml_extract_from_BTEQ(inp_filename):
    """
    BTEQ files are essentially ksh scripts, so for now we will simply call
    the ksh function to process those.
    """

    return dreml_extract_from_ksh(inp_filename)
