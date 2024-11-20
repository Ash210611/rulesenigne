# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===================================================================================

def check_r249():
    # -----------logical definitions ----------------------------------------------
    """
    Datamodel entity definition should not be same as entity name.
    """
    G.RULE_ID = 'r249'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ENTITY in G.ENTITIES:
        _val = G.ENTITY.entty_defn_txt
        _retval = 'PASS'

        if G.ENTITY.entty_nm == _val:
            _retval = 'FAIL'

        if _retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ENTITY',
                object_nm=G.ENTITY.entty_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0} definition must not contain only name of Entity'.format(G.ENTITY.entty_nm),
                class_object=G.ENTITY)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Entity:  {0} definition is verbose'.format(
                G.ENTITY.entty_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All entity definitions are verbose.')

    return 0
