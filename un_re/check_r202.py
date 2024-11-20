# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r202_for_1_table():
    """
    The attribute definition cannot be GT 256 characters.
    """

    found_an_issue = False

    if G.ATTRIB.attrib_defn_txt is None:

        found_an_issue = True

        report_firm_finding(
            object_type_nm='ATTRIB',
            object_nm=G.ATTRIB.entty_nm,
            severity=G.RULES[G.RULE_ID].severity,
            message='Attribute {0}.{1} definition is missing.'.format(
                G.ATTRIB.entty_nm,
                G.ATTRIB.attrib_nm),
            class_object=G.ATTRIB)

    elif len(G.ATTRIB.attrib_defn_txt) > 256:

        found_an_issue = True

        report_firm_finding(
            object_type_nm='ATTRIB',
            object_nm=G.ATTRIB.entty_nm,
            severity=G.RULES[G.RULE_ID].severity,
            message='Attribute {0}.{1} definition is > 256 charcters.'.format(
                G.ATTRIB.entty_nm,
                G.ATTRIB.attrib_nm),
            class_object=G.ATTRIB)
    else:
        G.COMMENT_STR = G.ATTRIB.attrib_defn_txt
        if not G.COMMENT_STR:  # if len (G.COMMENT_STR) == 0:

            found_an_issue = True

            report_firm_finding(
                object_type_nm='ATTRIB',
                object_nm=G.ATTRIB,
                severity=G.RULES[G.RULE_ID].severity,
                message='Attribute {0}.{1} definition has a blank comment.'.format(
                    G.ATTRIB.entty_nm,
                    G.ATTRIB.attrib_nm),
                class_object=G.ATTRIB)

    if not found_an_issue:
        if G.VERBOSE:
            G.LOGGER.debug((' ' * 15) + 'Good         : {0}.{1} attribute definition is not > 256 characters.'.format(
                G.ATTRIB.entty_nm,
                G.ATTRIB.attrib_nm))

    return found_an_issue


# ===============================================================================
def check_r203_for_1_table():
    """
    The column comment_str cannot be GT 256 characters.
    """

    found_an_issue = False

    if G.ATTRIB.colmn_cmmnt_txt is None:

        found_an_issue = True

        report_firm_finding(
            object_type_nm='ATTRIB',
            object_nm=G.ATTRIB.tbl_nm,
            severity=G.RULES[G.RULE_ID].severity,
            message='Column {0}.{1} has no comment.'.format(
                G.ATTRIB.tbl_nm,
                G.ATTRIB.colmn_nm),
            class_object=G.ATTRIB)

    elif len(G.ATTRIB.colmn_cmmnt_txt) == 0:

        found_an_issue = True

        report_firm_finding(
            object_type_nm='ATTRIB',
            object_nm=G.ATTRIB.colmn_cmmnt_txt,
            severity=G.RULES[G.RULE_ID].severity,
            message='Column {0}.{1} has a zero-length comment, which is not long enough.'.format(
                G.ATTRIB.tbl_nm,
                G.ATTRIB.colmn_nm),
            class_object=G.ATTRIB)
    else:
        G.COMMENT_STR = G.ATTRIB.colmn_cmmnt_txt
        if not G.COMMENT_STR:  # if len (G.COMMENT_STR) == 0:

            found_an_issue = True

            report_firm_finding(
                object_type_nm='ATTRIB',
                object_nm=G.ATTRIB,
                severity=G.RULES[G.RULE_ID].severity,
                message='Column {0}.{1} has a blank comment.'.format(
                    G.ATTRIB.tbl_nm,
                    G.ATTRIB.colmn_nm),
                class_object=G.ATTRIB)

    if not found_an_issue:
        if G.VERBOSE:
            G.LOGGER.debug(
                (' ' * 15) + 'Good         : {0}.{1} column comment is not greater than 256 characters.'.format(
                    G.ATTRIB.tbl_nm,
                    G.ATTRIB.colmn_nm))

    return found_an_issue


# ===============================================================================
def also_check_r203():
    # --physical  model validation----------------

    G.RULE_ID = 'r203'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_findings = 0

    for G.ATTRIB in G.ATTRIBS:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.ATTRIB.colmn_nm):
            continue

        if check_r203_for_1_table():
            num_findings += 1

    if num_findings > 1:
        indent_info('Notice       : {0} columns comments were > 256 characters.'.format(num_findings))

    elif num_findings == 1:
        indent_info('Notice       : {0} column comment was > 256 characters.'.format(num_findings))

    elif G.VERBOSE:
        indent_debug('Good         : No column comments are > 256 characters.')

    return


# ===============================================================================
def check_r202():
    # --Logical model validation----------------

    G.RULE_ID = 'r202'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_findings = 0

    for G.ATTRIB in G.ATTRIBS:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.ATTRIB.attrib_nm):
            continue

        if check_r202_for_1_table():
            num_findings += 1

    if num_findings > 1:
        indent_info('Notice       : {0} attributes defintions > 256 characters.'.format(num_findings))

    elif num_findings == 1:
        indent_info('Notice       : {0} attribute definition  was > 256 characters.'.format(num_findings))

    elif G.VERBOSE:
        indent_debug('Good         : No attributes have definitions > 256 characters.')

    also_check_r203()
