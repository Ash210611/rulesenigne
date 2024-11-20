# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r259_for_datamodel_table_names():
    """
    Datamodel Table Names must be unique.
    """
    # -----------physical names ---------------------------------------------

    G.RULE_ID = 'r260'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    tbl_list = []
    mod_name = []

    # check for duplicate entries in G.ENTITY.entty_nm
    for G.ENTITY in G.ENTITIES:
        tbl_list.append(G.ENTITY.tbl_nm)
        mod_name.append(G.ENTITY.model_nm)
    tbl_list.sort()
    _model_name = mod_name[0]

    for x in range(1, len(tbl_list)):
        retval = 0
        if tbl_list[x] == tbl_list[x - 1]:
            retval = retval + 1

        if retval > 1:
            report_firm_finding(
                object_type_nm='ENTITY',
                object_nm=tbl_list[x],
                severity=G.RULES[G.RULE_ID].severity,
                message='{0} must not contain duplicate table names: {1}'.format(_model_name, tbl_list[x]),
                class_object=G.ENTITY)
            num_findings += 1

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All models do not contain duplicate tables.')

    # ---------------------------------------
    return


# ===============================================================================
def check_r259():
    # -----------logical names ----------------------------------------------
    """
    Datamodel entity names should be unique.
    """
    G.RULE_ID = 'r259'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info(f'Checking rule {G.RULE_ID}...')

    num_findings = 0
    ent_list = []
    mod_name = []

    # check for duplicate entries in G.ENTITY.entty_nm
    for G.ENTITY in G.ENTITIES:
        ent_list.append(G.ENTITY.entty_nm)
        mod_name.append(G.ENTITY.model_nm)
    ent_list.sort()
    _model_name = mod_name[0]

    for x in range(1, len(ent_list)):
        retval = 0
        if ent_list[x] == ent_list[x - 1]:
            retval = retval + 1

        if retval > 1:
            report_firm_finding(
                object_type_nm='ENTITY',
                object_nm=ent_list[x],
                severity=G.RULES[G.RULE_ID].severity,
                message='{0} must not contain duplicate entity names: {1}'.format(_model_name, ent_list[x]),
                class_object=G.ENTITY)
            num_findings += 1

    if num_findings == 0:
        if G.VERBOSE:
            indent_debug('Good         : All entities do not contain duplicate entities.')

    check_r259_for_datamodel_table_names()
