# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r237():
    """
    Model Subject Area definitions should not be blank
    """
    G.RULE_ID = 'r237'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.SUBJCT_AREA in G.SUBJCT_AREAS:

        if G.SUBJCT_AREA.subjct_area_nm is None:
            continue
        # If the Subject Area Name is empty, do not check
        # the definition;

        if G.SUBJCT_AREA.subjct_area_defn_txt == '':
            report_firm_finding(
                object_type_nm='SUBJECT_AREA',
                object_nm=G.SUBJCT_AREA.subjct_area_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='Subject Area {0} has a blank definition.'.format(
                    G.SUBJCT_AREA.subjct_area_nm),
                class_object=G.SUBJCT_AREA)
            num_findings += 1

        elif G.VERBOSE:
            txt = G.SUBJCT_AREA.subjct_area_defn_txt[:20] + (G.SUBJCT_AREA.subjct_area_defn_txt[20:] and '...')

            indent_debug('Good         : Subject Area {0} definition is non-blank, is {1}'.format(
                G.SUBJCT_AREA.subjct_area_nm,
                txt))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All Model Subject Areas have non-blank definitions.')

    return 0
