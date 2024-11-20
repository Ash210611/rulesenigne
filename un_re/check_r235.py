# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r235():
    """
    Data Model name should be valid and not just a model number
    """
    G.RULE_ID = 'r235'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.MODEL in G.MODELS:

        if not G.MODEL.model_nm == G.MODEL.model_file_nm:
            report_firm_finding(
                object_type_nm='MODEL',
                object_nm=G.MODEL.model_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0} must match physical name of model: {1}'.format(
                    G.MODEL.model_nm,
                    G.MODEL.model_file_nm),
                class_object=G.MODEL)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Model:  {0} internal name is valid'.format(
                G.MODEL.model_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All models have valid internal name.')

    return 0
