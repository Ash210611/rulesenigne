import os

import un_re.global_shared_variables as G


# ===============================================================================
def antlr_create_logs_dir(grammar):
    logs_dir = G.SCRIPT_DIR + f'/un_re/Antlr/{grammar}_logs'

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
