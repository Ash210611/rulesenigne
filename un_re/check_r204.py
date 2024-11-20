# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===================================================================================
def check_r204_for_datamodel_physical_column_names():
    # -----------physical names ---------------------------------------------
    # Datamodel physical column name should not contain bad characters.

    G.RULE_ID = 'r205'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ATTRIB in G.ATTRIBS:
        val = G.ATTRIB.colmn_nm
        retval = 'PASS'

        for val_char in val:
            for bad_char in G.BAD_CHAR_LIST:
                if val_char == bad_char[0]:
                    retval = 'FAIL'
                    break

        if retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ATTRIB',
                object_nm=G.ATTRIB.colmn_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0}.{1} must not contain illegal characters in physical name'.format(
                    G.ATTRIB.tbl_nm,
                    G.ATTRIB.colmn_nm),
                class_object=G.ATTRIB)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Attribute: {0}.{1} does not contain illegal characters: {0}'.format(
                G.ATTRIB.tbl_nm,
                G.ATTRIB.colmn_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : No datamodel physical columns contain illegal characters in name.')

    return


# ===================================================================================
def check_r204():
    # -----------logical names ----------------------------------------------
    """
    Datamodel attribute name should not contain bad characters.
    """
    G.RULE_ID = 'r204'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ATTRIB in G.ATTRIBS:
        _val = G.ATTRIB.attrib_nm
        retval = 'PASS'
        for letter in _val:
            for bad_char in G.BAD_CHAR_LIST:
                if letter == chr(bad_char[0]):
                    retval = 'FAIL'
                    break

        if retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ATTRIB',
                object_nm=G.ATTRIB.attrib_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0}.{1} must not contain illegal characters'.format(
                    G.ATTRIB.entty_nm,
                    G.ATTRIB.attrib_nm),
                class_object=G.ATTRIB)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Attribute:  {0}.{1} does not contain illegal characters'.format(
                G.ATTRIB.entty_nm,
                G.ATTRIB.attrib_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All attributes do not contain illegal characters.')

    check_r204_for_datamodel_physical_column_names()
