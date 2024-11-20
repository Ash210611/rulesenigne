# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def also_check_r245():
    # -----------physical names -----------------------------------------------------
    # Datamodel physical table name should not contain bad characters.
    G.RULE_ID = 'r245'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ENTITY in G.ENTITIES:
        val = G.ENTITY.tbl_nm
        retval = 'PASS'

        for letter in val:
            for badChar in G.BAD_CHAR_LIST:
                if letter == badChar[0]:
                    retval = 'FAIL'
                    break

        if retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ENTITY',
                object_nm=G.ENTITY.entty_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0} must not contain illegal characters in physical name'.format(
                    G.ENTITY.tbl_nm),
                class_object=G.ENTITY)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Table:  does not contain illegal characters: {0}'.format(
                G.ENTITY.tbl_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All Tables do not contain illegal characters in name.')


# ===================================================================================
def check_r244():
    # -----------logical names ----------------------------------------------
    # Datamodel entity name should not contain bad characters.
    G.RULE_ID = 'r244'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ENTITY in G.ENTITIES:
        _val = G.ENTITY.entty_nm
        retval = 'PASS'
        for letter in _val:
            for badChar in G.BAD_CHAR_LIST:
                if letter == badChar[0]:
                    retval = 'FAIL'
                    break

        if retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ENTITY',
                object_nm=G.ENTITY.entty_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0} must not contain illegal characters'.format(
                    G.ENTITY.entty_nm),
                class_object=G.ENTITY)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Entity:  {0} does not contain illegal characters'.format(
                G.ENTITY.entty_nm))
    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All entities do not contain illegal characters.')
