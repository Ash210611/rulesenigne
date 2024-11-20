# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r232():
    """
    Model definitions should not be blank
    """
    G.RULE_ID = 'r232'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.MODEL in G.MODELS:

        if G.MODEL.model_defn_txt == '':
            report_firm_finding(
                object_type_nm='MODEL',
                object_nm=G.MODEL.model_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message=f'Model {G.MODEL.model_nm} has a blank definition.',
                class_object=G.MODEL)
            num_findings += 1

        elif G.VERBOSE:
            txt = G.MODEL.model_defn_txt[:20] + (G.MODEL.model_defn_txt[20:] and '...')

            indent_debug('Good         : Model {0} definition is non-blank, is {1}'.format(
                G.MODEL.model_nm,
                txt))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All models have non-blank definitions.')

    return 0
