# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r246_for_datamodel_physical_table_comments():
    """
    Datamodel physical table comment must not contain bad characters.
    """

    G.RULE_ID = 'r247'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ENTITY in G.ENTITIES:
        _val = G.ENTITY.tbl_cmmnt_txt
        _retval = 'PASS'

        if G.ENTITY.tbl_cmmnt_txt is None:
            indent_debug('Good       : Table: Comment does not contain illegal characters: {0}'.format(G.ENTITY.tbl_nm))
        else:
            for letter in _val:
                for bad_char in G.BAD_CHAR_LIST:
                    if letter == chr(bad_char[0]):
                        _retval = 'FAIL'
                        break

            if _retval == 'FAIL':
                report_firm_finding(
                    object_type_nm='ENTITY',
                    object_nm=G.ENTITY.tbl_nm,
                    severity=G.RULES[G.RULE_ID].severity,
                    message='{0} must not contain illegal characters in table comment'.format(G.ENTITY.tbl_nm),
                    class_object=G.ENTITY)
                num_findings += 1

            elif G.VERBOSE:
                indent_debug('Good         : Table:  Comment does not contain illegal characters: {0}'.format(
                    G.ENTITY.tbl_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All Tables do not contain illegal characters in Comment.')

    return 0


# ===============================================================================
def check_r246():
    # -----------logical definitions ----------------------------------------
    """
    Datamodel entity definition should not contain bad characters.
    """
    G.RULE_ID = 'r246'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ENTITY in G.ENTITIES:
        _val = G.ENTITY.entty_defn_txt
        _retval = 'PASS'
        for letter in _val:
            for bad_char in G.BAD_CHAR_LIST:
                if letter == chr(bad_char[0]):
                    _retval = 'FAIL'
                    break

        if _retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ENTITY',
                object_nm=G.ENTITY.entty_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0} definition must not contain illegal characters'.format(G.ENTITY.entty_nm),
                class_object=G.ENTITY)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Entity:  {0} definition does not contain illegal characters'.format(
                G.ENTITY.entty_nm))
    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All entity definitions do not contain illegal characters.')

    # -----------physical names -----------------------------------------------------
    check_r246_for_datamodel_physical_table_comments()
