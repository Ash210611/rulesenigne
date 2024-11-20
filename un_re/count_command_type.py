# ===============================================================================

import un_re.global_shared_variables as G


# ===============================================================================
def count_command_type(command_type):
    # traceback.print_stack ()

    if command_type in G.COMMAND_COUNTER:
        G.COMMAND_COUNTER[command_type] += 1
    else:
        G.COMMAND_COUNTER[command_type] = 1
    # If it exists, increment it, else initialize it.
