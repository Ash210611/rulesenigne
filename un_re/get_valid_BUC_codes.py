# pylint: disable=C0209			# Don't require formatted strings.

from collections import OrderedDict

import un_re.global_shared_variables as G
from un_re.indent import indent


# ===============================================================================
def get_valid_BUC_codes():
    '''
        For now this is reading from a static table.

        Ideally this should read from a dynamic source, maybe BRMS or
    Service Now
        '''

    if G.RULES_ENGINE_TYPE != 'ESP_RE':
        return

    inp_filename = G.SCRIPT_DIR + '/un_re/resources/valid_BUC_codes.lst'

    od = OrderedDict()

    with open(inp_filename, 'r', encoding='utf-8') as inp_file:
        for line in inp_file.readlines():
            if line.find('#') > -1:
                continue

            line = line.strip()
            od[line] = True

    G.VALID_BUC_CODE_LIST = list(sorted(od.keys()))

    if G.VERBOSE:
        num = len(G.VALID_BUC_CODE_LIST)
        if num == 1:
            indent('Read {0:5,d} valid BUC$ code.'.format(num))
        else:
            indent('Read {0:5,d} valid BUC$ codes.'.format(num))
