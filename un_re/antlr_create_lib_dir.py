import os

import un_re.global_shared_variables as G


# ===============================================================================
def antlr_create_lib_dir(grammar):
    lib_dir = G.SCRIPT_DIR + f'/un_re/Antlr/{grammar}_lib'

    if not os.path.exists(lib_dir):
        os.makedirs(lib_dir)
