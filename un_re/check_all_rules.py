import importlib
import os
import sys

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G


# ===============================================================================
def check_all_rules():
    # pprint_table_structures ()
    G.LOGGER.info('')
    G.LOGGER.info('=' * 88)
    G.LOGGER.info('Checking all rules...')

    if G.RULES_ENGINE_TYPE == 'ESP_RE':
        if G.COMMAND_COUNTER['ESP STATEMENT'] == 0:
            G.LOGGER.info('Wup, Checking no rules, as there are no ESP statements...')
            return

    elif G.RULES_ENGINE_TYPE != 'DATA_MODEL':
        if len(G.SQL_STATEMENT_OBJS) == 0 and len(G.INPUT_FILES) == 0:
            G.LOGGER.info('Wup, Checking no rules, as there are no SQL statements...')
            return

    sys.path.append(f"{os.path.join(G.SCRIPT_DIR, 'un_re')}")

    for rule_id in G.SHOULD_CHECK_RULE:
        module_name = f'check_{rule_id}'

        try:
            module = importlib.import_module(module_name)  # Import it.
        except ModuleNotFoundError:
            print(f'Failed to import {module_name}')
            print('\n')
            print(f'Current PATH: {sys.path}')
            print('\n')
            sys.exit(E.MODULE_NOT_FOUND)

        rule_function = getattr(module, module_name)

        rule_function()  # Run it.

    G.LOGGER.info('Done checking all rules.')
    return
