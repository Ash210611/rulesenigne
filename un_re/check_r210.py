# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===================================================================================

def check_r210():
    # -----------physical names -----------------------------------------------------
    """
    Datamodel physical column comment must not contain just the name of the column.
    """
    G.RULE_ID = 'r210'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    for G.ATTRIB in G.ATTRIBS:
        _val = G.ATTRIB.colmn_cmmnt_txt
        _retval = 'PASS'

        if G.ATTRIB.colmn_nm == _val:
            _retval = 'FAIL'

        if _retval == 'FAIL':
            report_firm_finding(
                object_type_nm='ATTRIB',
                object_nm=G.ATTRIB.colmn_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='{0}.{1} must not contain only name of the Column'.format(
                    G.ATTRIB.tbl_nm, G.ATTRIB.colmn_nm),
                class_object=G.ATTRIB)
            num_findings += 1

        elif G.VERBOSE:
            indent_debug('Good         : Column:  {0}.{1} Comment is verbose: {0}'.format(
                G.ATTRIB.tbl_nm,
                G.ATTRIB.colmn_nm))

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All Column comments are verbose.')

    return
