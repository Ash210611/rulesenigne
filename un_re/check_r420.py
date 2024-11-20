# pylint: disable=C0209           		# Don't require formtted strings
# pylint: disable=R0914				# Too many local variables
# pylint: disable=R0912				# Too many branches
# pylint: disable=R0915				# Too many statements

import re

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.print_msg import report_firm_finding


# ===============================================================================
def lookup_column_position(column_name):
    # print ('Looking up {0}'.format (column_name))

    for column_element in G.TABLE_STRUCTURE.column_elements:
        # print (column_element)
        if column_element.name_upper == column_name:
            # print ('Returning {0}'.format (column_element.position))
            return column_element.position

    return -1


# ===============================================================================
def check_r420_column(column_name, prev_column_pos, is_optional):
    found_issue = False

    this_pos = lookup_column_position(column_name)
    if this_pos == -1:
        if is_optional and G.VERBOSE:
            indent_debug('Notice       : Column {0}.{1} was not found, but it was optional anyway.'.format(
                G.TABLE_STRUCTURE.table_name_upper,
                column_name))
        else:
            found_issue = True
            report_firm_finding(
                object_type_nm='COLUMN NAME',
                object_nm=column_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='Column {0}.{1} was not found'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    column_name),
                class_object=G.TABLE_STRUCTURE)

    elif this_pos < prev_column_pos:
        # That won't be true if the prev column was not found.
        # If it wasn't found, key_pos == -1
        found_issue = True
        report_firm_finding(
            object_type_nm='COLUMN NAME',
            object_nm=column_name,
            severity=G.RULES[G.RULE_ID].severity,
            message='Column {0}.{1} was found out of order'.format(
                G.TABLE_STRUCTURE.table_name_upper,
                column_name),
            class_object=G.TABLE_STRUCTURE)

    elif G.VERBOSE and prev_column_pos > -1:
        indent_debug('Good         : Column {0}.{1} was found in order.'.format(
            G.TABLE_STRUCTURE.table_name_upper,
            column_name))

    return found_issue


# ===============================================================================
def check_KEY(num_problems_found):
    # Check the first column semi-manually
    key_name = G.TABLE_NAME + '_KEY'
    key_pos = lookup_column_position(key_name.upper())
    if key_pos == -1:
        num_problems_found += 1
        report_firm_finding(
            object_type_nm='COLUMN NAME',
            object_nm=key_name,
            severity=G.RULES[G.RULE_ID].severity,
            message='Column {0}.<table_name>_KEY was not found'.format(
                G.TABLE_STRUCTURE.table_name_upper),
            class_object=G.TABLE_STRUCTURE)
    # print ('key_name = {0}'.format (key_name))
    # print (G.TABLE_STRUCTURE)

    elif key_pos != 0:
        num_problems_found += 1
        # column_element	= G.TABLE_STRUCTURE.column_elements[key_pos]
        report_firm_finding(
            object_type_nm='COLUMN NAME',
            object_nm=key_name,
            severity=G.RULES[G.RULE_ID].severity,
            message='Column {0}.<table_name>_KEY was found out of order.'.format(
                G.TABLE_STRUCTURE.table_name_upper),
            class_object=G.TABLE_STRUCTURE)
        if G.VERBOSE:
            G.LOGGER.debug('{0}.{1} was found in position {2}'.format(
                G.TABLE_STRUCTURE.table_name_upper,
                key_name,
                key_pos))

    elif G.VERBOSE:
        indent_debug('Good         : Column <table_name>_KEY was found.')

    return num_problems_found, key_pos


# ===============================================================================
def check_r420_for_1_table():
    G.TABLE_NAME = G.TABLE_STRUCTURE.table_name_upper

    num_problems_found = 0

    (num_problems_found, key_pos) = check_KEY(num_problems_found)

    # -----------------------------------------------------------------------
    # Once the pattern is started, extend it to subsequent columns

    load_ctl_key_name = 'LOAD_CTL_KEY'
    load_ctl_key_pos = lookup_column_position(load_ctl_key_name)
    num_problems_found += check_r420_column(load_ctl_key_name, key_pos, False)

    cret_ts_name = 'CRET_TS'
    cret_ts_pos = lookup_column_position(cret_ts_name)
    num_problems_found += check_r420_column(cret_ts_name, load_ctl_key_pos, False)

    updt_ts_name = 'UPDT_TS'
    updt_ts_pos = lookup_column_position(updt_ts_name)
    num_problems_found += check_r420_column(updt_ts_name, cret_ts_pos, False)

    chnl_cd_name = 'CHNL_CD'
    chnl_cd_pos = lookup_column_position(chnl_cd_name)
    num_problems_found += check_r420_column(chnl_cd_name, updt_ts_pos, True)

    # -----------------------------------------------------------------------
    chnl_src_cd_name = 'CHNL_SRC_CD'
    chnl_src_cd_pos = lookup_column_position(chnl_src_cd_name)

    if chnl_src_cd_pos == -1:
        num_problems_found += 1
        report_firm_finding(
            object_type_nm='COLUMN NAME',
            object_nm=chnl_src_cd_name,
            severity=G.RULES[G.RULE_ID].severity,
            message='Column {0}.{1} was not found'.format(
                G.TABLE_STRUCTURE.table_name_upper,
                chnl_src_cd_name),
            class_object=G.TABLE_STRUCTURE)

    else:
        is_ok = True
        if chnl_cd_pos > -1:
            if chnl_src_cd_pos < chnl_cd_pos:
                num_problems_found += 1
                is_ok = False

                report_firm_finding(
                    object_type_nm='COLUMN NAME',
                    object_nm=chnl_src_cd_name,
                    severity=G.RULES[G.RULE_ID].severity,
                    message='Column {0}.{1} was found out of order'.format(
                        G.TABLE_STRUCTURE.table_name_upper,
                        chnl_src_cd_name),
                    class_object=G.TABLE_STRUCTURE)

        elif updt_ts_pos > -1:
            if chnl_src_cd_pos < updt_ts_pos:
                num_problems_found += 1
                is_ok = False
                report_firm_finding(
                    object_type_nm='COLUMN NAME',
                    object_nm=chnl_src_cd_name,
                    severity=G.RULES[G.RULE_ID].severity,
                    message='Column {0}.{1} was found out of order'.format(
                        G.TABLE_STRUCTURE.table_name_upper,
                        chnl_src_cd_name),
                    class_object=G.TABLE_STRUCTURE)

        if is_ok and G.VERBOSE:
            G.LOGGER.debug((' ' * 15) + 'Good         : Column {0}.{1} was found in order.'.format(
                G.TABLE_STRUCTURE.table_name_upper,
                chnl_src_cd_name))

    # -----------------------------------------------------------------------
    chk_sum_txt_name = 'CHK_SUM_TXT'
    chk_sum_txt_pos = lookup_column_position(chk_sum_txt_name)

    if chk_sum_txt_pos > -1:
        num_problems_found += check_r420_column(chk_sum_txt_name, chnl_src_cd_pos, True)

    # -----------------------------------------------------------------------
    rcd_eff_ts_name = 'RCD_EFF_TS'
    rcd_eff_ts_pos = lookup_column_position(rcd_eff_ts_name)

    if rcd_eff_ts_pos == -1:
        G.LOGGER.debug((' ' * 15) + 'Notice       : Column {0}.{1} was not found, but it was optional anyway.'.format(
            G.TABLE_STRUCTURE.table_name_upper,
            rcd_eff_ts_name))

    else:
        later_pos = max(chnl_src_cd_pos, chk_sum_txt_pos)

        if later_pos > -1:
            # then the order can be checked.
            if rcd_eff_ts_pos < later_pos:
                num_problems_found += 1
                report_firm_finding(
                    object_type_nm='COLUMN NAME',
                    object_nm=rcd_eff_ts_name,
                    severity=G.RULES[G.RULE_ID].severity,
                    message='Column {0}.{1} was found out of order'.format(
                        G.TABLE_STRUCTURE.table_name_upper,
                        rcd_eff_ts_name),
                    class_object=G.TABLE_STRUCTURE)
            elif G.VERBOSE:
                G.LOGGER.debug((' ' * 15) + 'Good         : Column {0}.{1} was found in order.'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    rcd_eff_ts_name))

    # -----------------------------------------------------------------------
    rcd_term_ts_name = 'RCD_TERM_TS'
    rcd_term_ts_pos = lookup_column_position(rcd_term_ts_name)

    if rcd_eff_ts_pos > -1:
        num_problems_found += check_r420_column(rcd_term_ts_name, rcd_eff_ts_pos, True)

    elif rcd_term_ts_pos > -1:
        num_problems_found += 1
        report_firm_finding(
            object_type_nm='COLUMN NAME',
            object_nm=rcd_term_ts_name,
            severity=G.RULES[G.RULE_ID].severity,
            message='Column {0}.{1} was found without finding the prerequisite column {2}'.format(
                G.TABLE_STRUCTURE.table_name_upper,
                rcd_term_ts_name,
                rcd_eff_ts_name),
            class_object=G.TABLE_STRUCTURE)

    # -----------------------------------------------------------------------
    curr_rcd_ind_name = 'CURR_RCD_IND'
    curr_rcd_ind_pos = lookup_column_position(curr_rcd_ind_name)

    if curr_rcd_ind_pos > -1:
        later_pos = max(chk_sum_txt_pos, chnl_src_cd_pos, rcd_term_ts_pos)

        if later_pos == -1:
            num_problems_found += 1
            report_firm_finding(
                object_type_nm='COLUMN NAME',
                object_nm=curr_rcd_ind_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='Column {0}.{1} was found without finding one of the prerequisite columns'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    curr_rcd_ind_name),
                class_object=G.TABLE_STRUCTURE)

        elif curr_rcd_ind_pos < later_pos:
            num_problems_found += 1
            report_firm_finding(
                object_type_nm='COLUMN NAME',
                object_nm=curr_rcd_ind_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='Column {0}.{1} was found out of order'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    curr_rcd_ind_name),
                class_object=G.TABLE_STRUCTURE)

        elif G.VERBOSE:
            G.LOGGER.debug((' ' * 15) + 'Good         : Column {0}.{1} was found in order.'.format(
                G.TABLE_STRUCTURE.table_name_upper,
                curr_rcd_ind_name))

    else:
        G.LOGGER.debug((' ' * 15) + 'Notice       : Column {0}.{1} was not found, but it was optional anyway.'.format(
            G.TABLE_STRUCTURE.table_name_upper,
            curr_rcd_ind_name))

    # -----------------------------------------------------------------------
    src_load_ctl_key_name = 'SRC_LOAD_CTL_KEY'
    src_load_ctl_key_pos = lookup_column_position(src_load_ctl_key_name)

    if src_load_ctl_key_pos == -1 and G.VERBOSE:
        G.LOGGER.debug((' ' * 15) + 'Notice       : Column {0}.{1} was not found, but it was optional anyway.'.format(
            G.TABLE_STRUCTURE.table_name_upper,
            src_load_ctl_key_name))
    else:
        if curr_rcd_ind_pos > -1:
            if src_load_ctl_key_pos < curr_rcd_ind_pos:
                num_problems_found += 1
                report_firm_finding(
                    object_type_nm='COLUMN NAME',
                    object_nm=src_load_ctl_key_name,
                    severity=G.RULES[G.RULE_ID].severity,
                    message='Column {0}.{1} was found out of order'.format(
                        G.TABLE_STRUCTURE.table_name_upper,
                        src_load_ctl_key_name),
                    class_object=G.TABLE_STRUCTURE)

            elif G.VERBOSE:
                G.LOGGER.debug((' ' * 15) + 'Good         : Column {0}.{1} was found in order.'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    src_load_ctl_key_name))
        else:
            num_problems_found += 1
            report_firm_finding(
                object_type_nm='COLUMN NAME',
                object_nm=src_load_ctl_key_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='Column {0}.{1} was found without finding the prerequisite column {2}'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    src_load_ctl_key_name,
                    curr_rcd_ind_name),
                class_object=G.TABLE_STRUCTURE)

    # -----------------------------------------------------------------------
    src_cret_ts_name = 'SRC_CRET_TS'
    src_cret_ts_pos = lookup_column_position(src_cret_ts_name)

    if src_cret_ts_pos == -1:
        if src_load_ctl_key_pos == -1 and G.VERBOSE:
            G.LOGGER.debug(
                (' ' * 15) + 'Notice       : Column {0}.{1} was not found, but it was optional anyway.'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    src_cret_ts_name))
        else:
            num_problems_found += 1
            report_firm_finding(
                object_type_nm='COLUMN NAME',
                object_nm=src_cret_ts_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='Column {0}.{1} was found without finding the associated column {2}'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    src_load_ctl_key_name,
                    src_cret_ts_name),
                class_object=G.TABLE_STRUCTURE)
    else:
        if src_load_ctl_key_pos == -1:
            num_problems_found += 1
            report_firm_finding(
                object_type_nm='COLUMN NAME',
                object_nm=src_cret_ts_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='Column {0}.{1} was found without finding the prerequisite column {2}'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    src_cret_ts_name,
                    src_load_ctl_key_name),
                class_object=G.TABLE_STRUCTURE)

        elif src_cret_ts_pos < src_load_ctl_key_pos:
            num_problems_found += 1
            report_firm_finding(
                object_type_nm='COLUMN NAME',
                object_nm=src_cret_ts_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='Column {0}.{1} was found out of order'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    src_cret_ts_name),
                class_object=G.TABLE_STRUCTURE)

        elif G.VERBOSE:
            G.LOGGER.debug((' ' * 15) + 'Good         : Column {0}.{1} was found in order.'.format(
                G.TABLE_STRUCTURE.table_name_upper,
                src_cret_ts_name))

    # -----------------------------------------------------------------------
    src_updt_ts_name = 'SRC_UPDT_TS'
    src_updt_ts_pos = lookup_column_position(src_updt_ts_name)

    if src_updt_ts_pos == -1:
        if src_load_ctl_key_pos == -1 and G.VERBOSE:
            G.LOGGER.debug(
                (' ' * 15) + 'Notice       : Column {0}.{1} was not found, but it was optional anyway.'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    src_updt_ts_name))
        else:
            num_problems_found += 1
            report_firm_finding(
                object_type_nm='COLUMN NAME',
                object_nm=src_updt_ts_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='Column {0}.{1} was found without finding the associated column {2}'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    src_load_ctl_key_name,
                    src_updt_ts_name),
                class_object=G.TABLE_STRUCTURE)
    else:
        if src_load_ctl_key_pos == -1:
            num_problems_found += 1
            report_firm_finding(
                object_type_nm='COLUMN NAME',
                object_nm=src_updt_ts_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='Column {0}.{1} was found without finding the prerequisite column {2}'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    src_updt_ts_name,
                    src_load_ctl_key_name),
                class_object=G.TABLE_STRUCTURE)

        elif src_updt_ts_pos < src_load_ctl_key_pos or src_updt_ts_pos < src_cret_ts_pos:
            num_problems_found += 1
            report_firm_finding(
                object_type_nm='COLUMN NAME',
                object_nm=src_updt_ts_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='Column {0}.{1} was found out of order'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    src_updt_ts_name),
                class_object=G.TABLE_STRUCTURE)

        elif G.VERBOSE:
            G.LOGGER.debug((' ' * 15) + 'Good         : Column {0}.{1} was found in order.'.format(
                G.TABLE_STRUCTURE.table_name_upper,
                src_updt_ts_name))

    # -----------------------------------------------------------------------
    latest_pos = max(
        src_updt_ts_pos,
        src_cret_ts_pos,
        src_load_ctl_key_pos,
        curr_rcd_ind_pos,
        rcd_term_ts_pos,
        rcd_eff_ts_pos,
        chk_sum_txt_pos)

    for column_element in G.TABLE_STRUCTURE.column_elements:
        # print ('Pos = {0}'.format (column_element.position))
        if column_element.position <= latest_pos:
            # print ('Skipping position {0} since latest_pos = {1}'.format (
            # 	column_element.position,
            # 	latest_pos))

            continue

        if column_element.name_upper == 'DEXL_CHNL_SRC_CD':
            # Don't check that column name, as it is a standard audit column
            continue

        if re.search(r'^.*\_CD', column_element.name_upper) and \
                not re.search(r'^SRC\_.*\_CD', column_element.name_upper):

            # G.LOGGER.debug ('Found CD column {0}'.format (column_element.name_upper))
            xxx_pos = column_element.position

            found_corresponding = False
            for second_element in G.TABLE_STRUCTURE.column_elements:
                if second_element.position <= xxx_pos:
                    continue

                if second_element.name_upper == 'SRC_' + column_element.name_upper:
                    if second_element.position == column_element.position + 1:
                        found_corresponding = True
                        G.LOGGER.debug((' ' * 15) + \
                                       'Good         : Found column {0}.{1} with the corresponding column {2}'.format(
                                           G.TABLE_STRUCTURE.table_name_upper,
                                           column_element.name_upper,
                                           second_element.name_upper))
                        latest_pos = second_element.position
                    else:
                        num_problems_found += 1
                        report_firm_finding(
                            object_type_nm='COLUMN NAME',
                            object_nm=column_element.name_upper,
                            severity=G.RULES[G.RULE_ID].severity,
                            message='Column {0}.{1} was gapped after {2} '.format(
                                G.TABLE_STRUCTURE.table_name_upper,
                                second_element.name_upper,
                                column_element.name_upper),
                            class_object=column_element)
                    break

            if not found_corresponding:
                xxx_name = column_element.name_upper.split('_')[0]
                num_problems_found += 1
                report_firm_finding(
                    object_type_nm='COLUMN NAME',
                    object_nm=column_element.name_upper,
                    severity=G.RULES[G.RULE_ID].severity,
                    message='Column {0}.{1} was missing the subsequent corresponding SRC_{2}_CD column'.format(
                        G.TABLE_STRUCTURE.table_name_upper,
                        column_element.name_upper,
                        xxx_name),
                    class_object=G.TABLE_STRUCTURE)

        elif re.search(r'^SRC\_.*\_CD', column_element.name_upper):
            xxx_name = column_element.name_upper.split('_')[1]
            num_problems_found += 1
            report_firm_finding(
                object_type_nm='COLUMN NAME',
                object_nm=column_element.name_upper,
                severity=G.RULES[G.RULE_ID].severity,
                message='Column {0}.{1} was missing the prerequisite {2}_CD column'.format(
                    G.TABLE_STRUCTURE.table_name_upper,
                    column_element.name_upper,
                    xxx_name),
                class_object=G.TABLE_STRUCTURE)

    # -----------------------------------------------------------------------
    if num_problems_found > 0:
        G.LOGGER.info((' ' * 15) + 'Notice       : Table {0} found {1} problems from rule {2}.'.format(
            G.TABLE_STRUCTURE.table_name_upper,
            num_problems_found,
            G.RULE_ID))
    elif G.VERBOSE:
        G.LOGGER.debug((' ' * 15) + 'Good         : Table {0} has all required fields.'.format(
            G.TABLE_STRUCTURE.table_name_upper))

    return num_problems_found > 0


# ===============================================================================
def check_r420():
    """
    This function checks that tables have the required audit columns, and
    that the optional audit columns are in the right order.
    """

    G.RULE_ID = 'r420'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_tables_with_issues = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
            return 0

        if G.TABLE_STRUCTURE.command_type in (
                'CREATE TABLE',
                'CREATE TABLE AS SELECT'):
            # Do not check this for ALTER TABLE commands
            continue

        if check_r420_for_1_table():
            num_tables_with_issues += 1

    return 0
