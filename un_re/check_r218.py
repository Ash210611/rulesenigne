# pylint: disable=C0209           # Don't require formatted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r218_for_datamodel_physical_column_names():
    """
    Datamodel physical column name should not contain articles.
    """

    G.RULE_ID = 'r219'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return
    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ATTRIB in G.ATTRIBS:
        _vals = G.ATTRIB.colmn_nm.split()  # split string into discrete words
        _retval = 'PASS'

        for val in _vals:
            for article in G.ARTICLE_LIST:
                if article == val.upper():
                    _retval = 'FAIL'
                    break

        if _retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ATTRIB',
                object_nm=G.ATTRIB.colmn_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0}.{1} must not contain articles in physical name'.format(
                    G.ATTRIB.tbl_nm, G.ATTRIB.colmn_nm),
                class_object=G.ATTRIB)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Articles not found found in column: {0}.{1}'.format(
                G.ATTRIB.tbl_nm,
                G.ATTRIB.attrib_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : No columns contain any articles.')

    return


# ===============================================================================
def check_r218():
    """
    Datamodel attribute name should not contain articles.
    """
    G.RULE_ID = 'r218'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    # -----------logical names
    num_findings = 0
    for G.ATTRIB in G.ATTRIBS:
        _vals = G.ATTRIB.attrib_nm.split()  # split string into discrete words
        _retval = 'PASS'

        for val in _vals:
            for article in G.ARTICLE_LIST:
                if article == val.upper():
                    _retval = 'FAIL'
                    break

        if _retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ATTRIB',
                object_nm=G.ATTRIB.attrib_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0}.{1} should not contain articles'.format(
                    G.ATTRIB.entty_nm, G.ATTRIB.attrib_nm),
                class_object=G.ATTRIB)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Attribute:  {0}.{1} does not contain articles in logical name'.format(
                G.ATTRIB.entty_nm,
                G.ATTRIB.attrib_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All attributes do not contain articles in logical name.')

    check_r218_for_datamodel_physical_column_names()
