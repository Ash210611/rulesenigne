# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r214():
    """
    Datamodel Attribute name should not match the physical column name
    """
    G.RULE_ID = 'r214'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ATTRIB in G.ATTRIBS:

        if G.ATTRIB.attrib_nm == G.ATTRIB.colmn_nm:
            report_firm_finding(
                object_type_nm='ATTRIB',
                object_nm=G.ATTRIB.attrib_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0}.{1} should not match the physical colmn name: {2}.{3}'.format(
                    G.ATTRIB.entty_nm, G.ATTRIB.attrib_nm, G.ATTRIB.tbl_nm, G.ATTRIB.colmn_nm),
                class_object=G.ENTITY)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Attribute:  {0}.{1} does not match physical column name'.format(
                G.ATTRIB.entty_nm,
                G.ATTRIB.attrib_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All attributes do not match column names.')

    return 0
