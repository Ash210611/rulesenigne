# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===================================================================================

def check_r250():
    # -----------physical names -----------------------------------------------------
    """
    Datamodel physical table comment must not contain just the name of the table.
    """
    G.RULE_ID = 'r250'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ENTITY in G.ENTITIES:
        _val = G.ENTITY.tbl_cmmnt_txt
        _retval = 'PASS'

        if G.ENTITY.tbl_nm == _val:
            _retval = 'FAIL'

        if _retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ENTITY',
                object_nm=G.ENTITY.tbl_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0} must not contain only name of the Table'.format(G.ENTITY.tbl_nm),
                class_object=G.ENTITY)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Table:  Comment is verbose: {0}'.format(
                G.ENTITY.tbl_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All Tables comments are verbose.')
    # ----------------------------------

    return 0
