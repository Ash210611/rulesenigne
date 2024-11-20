# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r254():
    """
    Datamodel Entity name should not match the physical table name
    """
    G.RULE_ID = 'r254'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ENTITY in G.ENTITIES:

        if G.ENTITY.entty_nm == G.ENTITY.tbl_nm:
            report_firm_finding(
                object_type_nm='ENTITY',
                object_nm=G.ENTITY.entty_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0} should not match the physical table name: {1}'.format(
                    G.ENTITY.entty_nm,
                    G.ENTITY.tbl_nm),
                class_object=G.ENTITY)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Entity:  {0} does not match physical table name'.format(
                G.ENTITY.entty_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All entities do not match table names.')

    return 0
