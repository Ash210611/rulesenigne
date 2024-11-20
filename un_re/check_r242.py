# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.indent_warning import indent_warning
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r242_for_one_entity():
    # print (G.ENTITY)	# For debugging purposes

    max_length = 255  # Consider setting that length as a global variable.

    found_an_issue = False
    if G.ENTITY.entty_nm_tokens[0] == 'WRK':
        if G.VERBOSE:
            indent_debug(f'Skipping {G.ENTITY.entty_nm} for a Work entity')
        return found_an_issue

    if G.ENTITY.entty_nm_tokens[0] in ('TEMP', 'TMP'):
        if G.VERBOSE:
            indent_debug(f'Skipping {G.ENTITY.entty_nm} for a Temp entity')
        return found_an_issue

    if len(G.ENTITY.entty_defn_txt) > max_length:
        report_firm_finding(
            object_type_nm='ENTITY',
            object_nm=G.ENTITY.entty_nm,
            severity=G.RULES[G.RULE_ID].severity,
            message='Entity: {0} has a definition length of {1} characters.'.format(
                G.ENTITY.entty_nm,
                len(G.ENTITY.entty_defn_txt)),
            class_object=G.ENTITY)

        indent_warning('Entity Defntn: {0}'.format(G.ENTITY.entty_defn_txt[0:50] + '..., etc.'))
        indent_warning('Max length   : {0}'.format(max_length))
        found_an_issue = True

    elif G.VERBOSE:
        indent_debug('Good         : Entity: {0} has definition length of {1}'.format(
            G.ENTITY.entty_nm,
            len(G.ENTITY.entty_defn_txt)))

    return found_an_issue


# ===============================================================================
def check_r243_for_one_entity():
    # print (G.ENTITY)      # For debugging purposes

    max_length = 255  # Consider setting that length as a global variable.

    found_an_issue = False

    if len(G.ENTITY.tbl_cmmnt_txt) > max_length:
        report_firm_finding(
            object_type_nm='ENTITY',
            object_nm=G.ENTITY.entty_nm,
            severity=G.RULES[G.RULE_ID].severity,
            message='Entity: {0} has a comment length of {1} characters.'.format(
                G.ENTITY.tbl_nm,
                len(G.ENTITY.tbl_cmmnt_txt)),
            class_object=G.ENTITY)

        indent_warning('Table Defntn : {0}'.format(G.ENTITY.entty_defn_txt[0:50] + '..., etc.'))
        indent_warning('Max length   : {0}'.format(max_length))
        found_an_issue = True

    elif G.VERBOSE:
        indent_debug('Good         : Table : {0} has comment length of {1}'.format(
            G.ENTITY.tbl_nm,
            len(G.ENTITY.tbl_cmmnt_txt)))

    return found_an_issue


# ===============================================================================
def check_r242_for_datamodel_physical_comments():
    """
    Table comment must be less than 255 characters long.
    """
    # ----------------check physical comment

    G.RULE_ID = 'r243'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_findings = 0
    for G.ENTITY in G.ENTITIES:

        if check_r243_for_one_entity():
            num_findings += 1

    if num_findings == 0:
        indent_info('Good         : All Tables have comment length of < 255 characters.')
    elif num_findings == 1:
        indent_info('Notice       : Found {0} table comments with a definition length too long.'.format(num_findings))
    elif num_findings > 1:
        indent_info('Notice       : Found {0} table comments with a definition length too long.'.format(num_findings))

    return


# ===============================================================================
def check_r242():
    # ----------------check logical defintion
    """
    Entity definitions should be less than 255 characters long.
    """
    G.RULE_ID = 'r242'

    # -----------------------------------------------------------------------
    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_findings = 0
    for G.ENTITY in G.ENTITIES:

        if check_r242_for_one_entity():
            num_findings += 1

    if num_findings == 0:
        indent_info('Good         : All Entities have definition length of < 255 characters.')
    elif num_findings == 1:
        indent_info(
            'Notice       : Found {0} Entity definitions with a definition length too long.'.format(num_findings))
    elif num_findings > 1:
        indent_info(
            'Notice       : Found {0} Entity definitions with a definition length too long.'.format(num_findings))

    check_r242_for_datamodel_physical_comments()
