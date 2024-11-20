# pylint: disable=C0209			# Don't require formatted strings.

import un_re.global_shared_variables as G


# ======== ========= ========= ========= ========= ========= ========= ==========
def print_command_summary():
    G.LOGGER.info('Command Summary:')

    command_len = 0

    try:
        for key in sorted(G.COMMAND_COUNTER.keys()):
            command_len = max(command_len, len(key))
    except:
        print(G.COMMAND_COUNTER)
        raise

    pr_format = r'{{0}} Num {{1:{0}s}} commands: {{2:4d}}'.format(
        command_len)

    for key in sorted(G.COMMAND_COUNTER.keys()):
        G.LOGGER.info(pr_format.format(
            (' ' * 14),
            key,
            G.COMMAND_COUNTER[key]))
