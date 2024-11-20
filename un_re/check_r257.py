# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def also_check_r258():
    # -----------physical names
    # Datamodel physical table name should not contain articles.
    G.RULE_ID = 'r258'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return
    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ENTITY in G.ENTITIES:
        _val = G.ENTITY.tbl_nm.split()  # split string into discrete words
        _retval = 'PASS'

        for token in _val:
            for article in G.ARTICLE_LIST:
                if article.article_nm == token.upper():
                    _retval = 'FAIL'
                    break

        if _retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ENTITY',
                object_nm=G.ENTITY.entty_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0} must not contain articles in physical name'.format(G.ENTITY.tbl_nm),
                class_object=G.ENTITY)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Table:  does not contain articles in name: {0}'.format(
                G.ENTITY.tbl_nm))
    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All Tables do not contain articles name.')


# ===============================================================================
def check_r257():
    """
    Datamodel entity name should not contain articles.
    """
    G.RULE_ID = 'r257'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    # -----------logical names
    num_findings = 0
    for G.ENTITY in G.ENTITIES:
        _val = []
        _val = G.ENTITY.entty_nm.split()  # split string into discrete words
        _retval = 'PASS'

        for token in _val:
            for article in G.ARTICLE_LIST:
                if article.article_nm == token:
                    _retval = 'FAIL'
                    break

        if _retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ENTITY',
                object_nm=G.ENTITY.entty_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0} should not contain articles'.format(G.ENTITY.entty_nm),
                class_object=G.ENTITY)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Entity:  {0} does not contain articles in logical name'.format(
                G.ENTITY.entty_nm))
    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All entities do not contain articles in logical name.')

    also_check_r258()

    return 0
