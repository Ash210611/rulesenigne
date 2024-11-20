# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===================================================================================

def check_r256():
    # -----------logical definitions ----------------------------------------------
    """
    Datamodel Table Domain must be listed.
    """
    G.RULE_ID = 'r256'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ENTITY in G.ENTITIES:
        _retval = 'PASS'

        try:
            if len(G.ENTITY.DataDomain_udp) < 1:
                _retval = 'FAIL'

        except TypeError:
            _retval = 'FAIL'

        if _retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ENTITY',
                object_nm=G.ENTITY.entty_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0} must have Data Domain'.format(G.ENTITY.entty_nm),
                class_object=G.ENTITY)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Entity:  {0} has Data Domain: {1}'.format(
                G.ENTITY.entty_nm, G.ENTITY.DataDomain_udp))
    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All entities have Data Domains.')

    return
