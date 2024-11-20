import resource

import un_re.global_shared_variables as G


# ===============================================================================
def get_memory_used():
    if G.SYSTEM_OS == 'Windows':
        return 0

    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
