# pylint: disable=C0209         # Don't require formtted strings
# pylint: disable=C0301		# Allow long lines

import re

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r233():
    """
    Data Model Name cannot have bad characters.
    """
    G.RULE_ID = 'r233'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.MODEL in G.MODELS:
        # print (f'G.MODEL.nsm_file_nm={G.MODEL.nsm_file_nm}')

        if not re.match(r'^[A-Za-z0-9_ ]', G.MODEL.nsm_file_nm):
            report_firm_finding(
                object_type_nm='MODEL',
                object_nm=G.MODEL.model_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='Model name must not have special characters.(only A-Z,a-z,0-9,_, <space>)',
                class_object=G.MODEL)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Model:  {0} does not have bad characters in model name.'.format(
                G.MODEL.model_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All models have valid model names.')

    return
