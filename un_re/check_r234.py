# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r234():
    """
    Data Model name should be complete sentence not just model name.
    """
    G.RULE_ID = 'r234'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.MODEL in G.MODELS:

        if (G.MODEL.model_defn_txt == G.MODEL.model_nm) or \
                not G.MODEL.model_defn_txt.upper().find('TEMPLATE') == -1:

            report_firm_finding(
                object_type_nm='MODEL',
                object_nm=G.MODEL.model_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='Model {0} definition must be full sentence: {1}'.format(
                    G.MODEL.model_nm,
                    G.MODEL.model_defn_txt[0:25]),
                class_object=G.MODEL)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Model: {0} definition is full sentence'.format(
                G.MODEL.model_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All models have valid definition.')

    return 0
