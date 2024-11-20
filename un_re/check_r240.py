# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.indent_warning import indent_warning
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r240_for_one_entity():
    # print (G.ENTITY)	# For debugging purposes

    found_an_issue = False

    if G.ENTITY.entty_nm_tokens[0] == 'WRK':
        if G.VERBOSE:
            indent_debug(f'Skipping {G.ENTITY.entty_nm} for a Work entity')
            return found_an_issue

    if G.ENTITY.entty_nm_tokens[0] in ('TEMP', 'TMP'):
        if G.VERBOSE:
            indent_debug(f'Skipping {G.ENTITY.entty_nm} for a Temp entity')
            return found_an_issue

    if G.ENTITY.entty_defn_txt is None:
        found_an_issue = True

        report_firm_finding(
            object_type_nm='ENTITY',
            object_nm=G.ENTITY.entty_nm,
            severity=G.RULES[G.RULE_ID].severity,
            message='Entity: {0} has no definition.'.format(
                G.ENTITY.entty_nm),
            class_object=G.ENTITY)

        indent_warning('Entity Defntn: Is Empty')

    elif len(G.ENTITY.entty_defn_txt) < 1:
        found_an_issue = True
        report_firm_finding(
            object_type_nm='ENTITY',
            object_nm=G.ENTITY.entty_nm,
            severity=G.RULES[G.RULE_ID].severity,
            message='Entity: {0} has no definition.'.format(
                G.ENTITY.entty_nm),
            class_object=G.ENTITY)
        indent_warning(
            'Entity  : {0} Definition is empty'.format(G.ENTITY.entty_nm))

    elif G.VERBOSE:
        indent_debug('Good         : Entity: {0} has a definition'.format(
            G.ENTITY.entty_nm))

    return found_an_issue


# ===============================================================================
def check_r241_for_one_entity():
    found_an_issue = False

    if G.ENTITY.tbl_cmmnt_txt is None:
        report_firm_finding(
            object_type_nm='ENTITY',
            object_nm=G.ENTITY.entty_nm,
            severity=G.RULES[G.RULE_ID].severity,
            message='Table:  {0} has no comment.'.format(
                G.ENTITY.tbl_nm),
            class_object=G.ENTITY)

        indent_warning('Table Comment: Is Empty')

        found_an_issue = True
    elif len(G.ENTITY.tbl_cmmnt_txt) < 1:
        report_firm_finding(
            object_type_nm='ENTITY',
            object_nm=G.ENTITY.entty_nm,
            severity=G.RULES[G.RULE_ID].severity,
            message='Table: {0} has no comment.'.format(
                G.ENTITY.tbl_nm),
            class_object=G.ENTITY)

        indent_warning('Table Comment: <empty>}')

        found_an_issue = True

    elif G.VERBOSE:
        indent_debug('Good         : Table : {0} has comment'.format(
            G.ENTITY.tbl_nm))

    return found_an_issue


# ===============================================================================
def also_check_r241():
    # ----------------check physical comment
    # Table comment must not be empty.
    G.RULE_ID = 'r241'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_findings = 0
    for G.ENTITY in G.ENTITIES:

        if check_r241_for_one_entity():
            num_findings += 1

    if num_findings == 0:
        indent_info('Good         : All Tables have comments.')
    elif num_findings == 1:
        indent_info('Notice       : Found {0} table with no comment.'.format(num_findings))
    elif num_findings > 1:
        indent_info('Notice       : Found {0} tables with no comments.'.format(num_findings))


# ===============================================================================
def check_r240():
    # ----------------check logical defintion
    """
    Entity definitions must not be empty.
    """
    G.RULE_ID = 'r240'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_findings = 0
    for G.ENTITY in G.ENTITIES:

        if check_r240_for_one_entity():
            num_findings += 1

    if num_findings == 0:
        indent_info('Good         : All Entities have definitions.')
    elif num_findings == 1:
        indent_info('Notice       : Found {0} Entity with no definition.'.format(num_findings))
    elif num_findings > 1:
        indent_info('Notice       : Found {0} Entities with no definitions.'.format(num_findings))

    also_check_r241()
