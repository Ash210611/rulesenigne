# pylint: disable=C0209           # Don't require formtted strings


import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r208():
    """
    Datamodel attribute name should contain no underscores.
    """
    G.RULE_ID = 'r208'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ATTRIB in G.ATTRIBS:

        if not G.ATTRIB.attrib_nm.find('_') == -1:
            report_firm_finding(
                object_type_nm='ATTRIB',
                object_nm=G.ATTRIB.attrib_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='Attribute Name must not contain undersocres: {0}'.format(
                    G.ATTRIB.attrib_nm),
                class_object=G.ATTRIB)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Attribute:  {0}.{1} name has no underscores'.format(
                G.ATTRIB.entty_nm,
                G.ATTRIB.attrib_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All attributes have no underscores in name.')

    return 0
