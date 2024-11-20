# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===================================================================================

def check_r209():
    # -----------logical definitions ----------------------------------------------
    """
    Datamodel attribute definition should not be same as attribute name.
    """
    G.RULE_ID = 'r209'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ATTRIB in G.ATTRIBS:
        _val = G.ATTRIB.attrib_defn_txt
        _retval = 'PASS'

        if G.ATTRIB.attrib_nm == _val:
            _retval = 'FAIL'

        if _retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ATTRIB',
                object_nm=G.ATTRIB.attrib_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0}.{1} definition must not contain only name of Entity'.format(
                    G.ATTRIB.entty_nm, G.ATTRIB.attrib_nm),
                class_object=G.ATTRIB)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Attribute:  {0}.{1} definition is verbose'.format(
                G.ATTRIB.entty_nm,
                G.ATTRIB.attrib_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All attribute definitions are verbose.')

    return
