# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r248():
    """
    Datamodel entity name should contain no underscores.
    """
    G.RULE_ID = 'r248'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ENTITY in G.ENTITIES:

        if not G.ENTITY.entty_nm.find('_') == -1:
            report_firm_finding(
                object_type_nm='ENTITY',
                object_nm=G.ENTITY.entty_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='Entity Name must not contain underscores: {0}'.format(
                    G.ENTITY.entty_nm),
                class_object=G.ENTITY)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Entity:  {0} name has no underscores'.format(
                G.ENTITY.entty_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All entities have no underscores in name.')

    return
