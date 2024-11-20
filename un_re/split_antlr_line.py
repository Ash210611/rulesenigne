# ===============================================================================
def split_antlr_line(line):
    """
    Given an input line from the Anltr log like this:
        Found relation source        : Some_DB.GRPR_EBM_LAST_SVC_DT_PROFSomething
    this function should return the contents after the colon
    """

    line = line.split(':')[1]
    line = line.strip()

    return line
