# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r206_for_physical_column_names():
    # -----------physical names ---------------------------------------------
    # Datamodel physical column comment must not contain bad characters.

    G.RULE_ID = 'r207'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ATTRIB in G.ATTRIBS:
        _val = G.ATTRIB.colmn_cmmnt_txt
        _retval = 'PASS'

        for val_char in _val:
            for bad_char in G.BAD_CHAR_LIST:
                if val_char == bad_char[0]:
                    _retval = 'FAIL'
                    break

        if _retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ATTRIB',
                object_nm=G.ATTRIB.colmn_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0}.{1} must not contain illegal characters in table comment'.format(
                    G.ATTRIB.tbl_nm, G.ATTRIB.colmn_nm),
                class_object=G.ATTRIB)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Column: {0}.{1} Comment does not contain illegal characters: {0}'.format(
                G.ATTRIB.tbl_nm, G.ATTRIB.colmn_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All Columns do not contain illegal characters in Comment.')


# ===============================================================================
def check_r206():
    """
    Datamodel attribute definition should not contain bad characters.
    """

    # -----------logical definitions ----------------------------------------
    G.RULE_ID = 'r206'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ATTRIB in G.ATTRIBS:
        _val = G.ATTRIB.attrib_defn_txt
        _retval = 'PASS'
        for letter in _val:
            for bad_char in G.BAD_CHAR_LIST:
                if letter == chr(bad_char[0]):
                    _retval = 'FAIL'
                    break

        if _retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ATTRIB',
                object_nm=G.ATTRIB.attrib_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0}.{1} definition must not contain illegal characters'.format(
                    G.ATTRIB.entty_nm, G.ATTRIB.attrib_nm),
                class_object=G.ATTRIB)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Attribute:  {0}.{1} definition does not contain illegal characters'.format(
                G.ATTRIB.entty_nm, G.ATTRIB.attrib_nm))
    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All attribute definitions do not contain illegal characters.')

    check_r206_for_physical_column_names()
