# pylint: disable=C0209         # Don't require formtted strings
# pylint: disable=C0301		# Allow long lines

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r239():
    """
    Model Subject Area definitions must be full sentence
    """
    G.RULE_ID = 'r239'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    num_empty_subject_areas = 0
    for G.SUBJCT_AREA in G.SUBJCT_AREAS:
        if G.SUBJCT_AREA.subjct_area_nm is None:
            num_empty_subject_areas += 1
            # Cannot check the definition if the name is empty.
            # Something is not right if that happens.
            # print an error about this??
            continue

        _val = G.SUBJCT_AREA.subjct_area_nm

        if G.SUBJCT_AREA.subjct_area_defn_txt == _val:
            report_firm_finding(
                object_type_nm='SUBJECT_AREA',
                object_nm=G.SUBJCT_AREA.subjct_area_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='Subject Area {0} definition cannot just contain name of Subj Area.'.format(
                    G.SUBJCT_AREA.subjct_area_nm),
                class_object=G.SUBJCT_AREA)
            num_findings += 1

        elif G.VERBOSE:
            txt = G.SUBJCT_AREA.subjct_area_defn_txt[:20] + (G.SUBJCT_AREA.subjct_area_defn_txt[20:] and '...')

            indent_debug('Good         : Subject Area {0} definition is verbose, is {1}'.format(
                G.SUBJCT_AREA.subjct_area_nm,
                txt))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All Model Subject Area definition are verbose.')

    return 0
