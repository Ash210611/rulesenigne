# pylint: disable=C0209           		# Don't require formtted strings
# pylint: disable=R0912				# Too many branches

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
def join_part_list(part_list):
    new_name = part_list[0]

    for part in part_list[1:]:
        new_name = new_name + '_' + part

    return new_name


# ===============================================================================
def lookfor_column_name(part_list, period_endpoint, lookfor_endpoint_list):
    found = False
    for part_num, part in enumerate(part_list):

        if part == period_endpoint:
            for lookfor_endpoint in lookfor_endpoint_list:

                part_list[part_num] = lookfor_endpoint

                column_name_to_lookfor = join_part_list(part_list)
                for column_element in G.COLUMN_ELEMENTS:
                    if column_element.name_upper == column_name_to_lookfor:
                        found = True
                        break
                if not found:
                    if G.VERBOSE:
                        indent_debug(
                            f'Notice       : Did not find endpoint pair: {column_name_to_lookfor}')
                else:
                    if G.VERBOSE:
                        indent_debug(
                            f'Good         : Found endpoint pair: {column_name_to_lookfor}')
                    break
            break

    if not found:
        report_adjustable_finding(
            object_type_nm='COLUMN',
            object_nm=G.COLUMN_NAME,
            normal_severity=G.RULES[G.RULE_ID].severity,
            normal_message='Column {0} is missing an endpoint pair'.format(
                G.COLUMN_NAME),
            adjusted_message='Accepting missing endpoint pair in ruleset {0}'.format(
                G.TABLE_STRUCTURE.ruleset),
            class_object=G.TABLE_STRUCTURE)

    return not found


# ===============================================================================
def find_first_period_endpoint(reversed_part_list):
    '''
    Period endpoints may occur at different positions.
    '''

    for part in reversed_part_list:
        if part in ['BEG', 'C', 'CAN', 'EFF', 'END', 'EXPIRN',
                    'START', 'TERM', 'TRM', 'TRMNTN']:
            return part  # Return the first part matched

    return ''


# ===============================================================================
def check_r419_for_1_column():
    num_problems_found = 0

    if G.COLUMN_ELEMENT.name_upper in ('CRET_TS', 'UPDT_TS'):
        # Don't bother checking these column names
        return num_problems_found  # return 0

    if G.COLUMN_ELEMENT.classword in (
            'DT',
            'TS'):

        indent_info('Column name  : {0}'.format(G.COLUMN_ELEMENT.name_upper))

        G.COLUMN_NAME = G.COLUMN_ELEMENT.name_upper

        part_list = G.COLUMN_ELEMENT.column_name_tokens
        # print (part_list)

        if len(part_list) == 1:
            return 0
        # There will not be a period type

        reversed_part_list = list(reversed(part_list))
        # print (reversed_part_list)

        period_endpoint = find_first_period_endpoint(reversed_part_list)

        # Checkable period endpoint pairs include
        # BEG and END
        # EFF and TERM
        # START and END

        if period_endpoint == '':
            if G.VERBOSE:
                indent_debug('Notice       : For column {0}, no period endpoint found.'.format(
                    G.COLUMN_NAME))
                return 0
        else:
            if G.VERBOSE:
                indent_debug('Notice       : Found starting endpoint {0}'.format(
                    period_endpoint))

        lookfor_endpoint_list = []  # to start with

        if period_endpoint == 'BEG':
            lookfor_endpoint_list = ['END']

        elif period_endpoint in ['CAN', 'C']:
            lookfor_endpoint_list = ['START']

        elif period_endpoint == 'END':
            lookfor_endpoint_list = ['BEG', 'START']

        elif period_endpoint == 'EFF':
            lookfor_endpoint_list = ['EXPIRN', 'TERM', 'TRM', 'TRMNTN']

        elif period_endpoint == 'EXPIRN':
            lookfor_endpoint_list = ['EFF']

        elif period_endpoint == 'START':
            lookfor_endpoint_list = ['END', 'CAN', 'C']

        elif period_endpoint in ['TERM', 'TRM', 'TRMNTN']:
            lookfor_endpoint_list = ['EFF']

        else:
            indent_debug('Unexpected period_endpoint: {0}'.format(period_endpoint))

        if G.VERBOSE:
            if len(lookfor_endpoint_list) == 0:
                indent_debug((' ' * 15) + 'Unexpectedly empty lookfor_endpoint_list')
                print(G.TABLE_STRUCTURE)
                return 0

            if len(lookfor_endpoint_list) == 1:
                indent_debug((' ' * 15) + 'Found {0}, will look for {1}'.format(
                    period_endpoint,
                    lookfor_endpoint_list[0]))
            else:
                indent_debug((' ' * 15) + 'Found {0}, will look for one of {1}'.format(
                    period_endpoint,
                    lookfor_endpoint_list))

        if lookfor_column_name(part_list, period_endpoint, lookfor_endpoint_list):
            num_problems_found += 1

    return num_problems_found


# ===============================================================================
def check_r419_for_1_table():
    num_columns_with_issues = 0

    if G.TABLE_STRUCTURE.command_type not in (
            'CREATE TABLE',
            'ALTER TABLE COLUMN'):
        return num_columns_with_issues

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME, G.TABLE_STRUCTURE.table_name_upper):
        return num_columns_with_issues

    if len(G.TABLE_STRUCTURE.table_name_tokens) > 0:
        if G.TABLE_STRUCTURE.table_name_tokens[0].upper() in ('W', 'TEMP', 'TMP'):
            # Skip this rule for work tables.
            indent_debug('Notice-{0}  : Skipping {0} for a Work table.'.format(G.RULE_ID))
            return num_columns_with_issues

    G.COLUMN_ELEMENTS = G.TABLE_STRUCTURE.column_elements

    for G.COLUMN_ELEMENT in G.COLUMN_ELEMENTS:
        if check_for_rule_exception(G.RULE_ID,
                                    G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper,
                                    G.COLUMN_ELEMENT.name_upper):
            continue

        if check_r419_for_1_column() > 0:
            num_columns_with_issues += 1

    if num_columns_with_issues > 1:
        indent_info('Notice-{0}  : Table {1} has {2} columns with time-period endpoint issues.'.format(
            G.RULE_ID,
            G.TABLE_STRUCTURE.table_name_upper,
            num_columns_with_issues))
    elif num_columns_with_issues == 1:
        indent_info('Notice-{0}  : Table {1} has {2} column with a time-period endpoint issue.'.format(
            G.RULE_ID,
            G.TABLE_STRUCTURE.table_name_upper,
            num_columns_with_issues))
    elif G.VERBOSE:
        num_column_elements = len(G.TABLE_STRUCTURE.column_elements)
        if num_column_elements == 1:
            indent_debug('Good         : Table {0} has {1} column with no issues with time-period endpoints.'.format(
                G.TABLE_STRUCTURE.table_name_upper,
                len(G.COLUMN_ELEMENTS)))
        elif num_column_elements > 1:
            indent_debug('Good         : Table {0} has {1} columns with no issues with time-period endpoints.'.format(
                G.TABLE_STRUCTURE.table_name_upper,
                len(G.COLUMN_ELEMENTS)))

    return num_columns_with_issues


# ===============================================================================
def check_r419():
    """
    This function checks that tables have the required audit columns, and
    that the optional audit columns are in the right order.
    """

    G.RULE_ID = 'r419'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    # Check the rule now that the prerequisites are passed.
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_tables_with_issues = 0

    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:
        if check_r419_for_1_table() > 0:
            num_tables_with_issues += 1

    if num_tables_with_issues == 1:
        indent_info('Notice-{0}  : {1} table has issues with time-period endpoints'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif num_tables_with_issues > 1:
        indent_info('Notice-{0}  : {1} tables have issues with time-period endpoints.'.format(
            G.RULE_ID,
            num_tables_with_issues))
    elif G.VERBOSE:
        indent_debug('Good         : No tables have issues with time-period endpoints.')

    return 0
