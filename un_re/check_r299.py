# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# pylint: disable-msg=too-many-arguments
# The check_r299_report function needs quite a few arguments.
# It would add not value to group into a class just to satisfy pylint here.

# ===============================================================================
def check_r299_report(
        database_base_upper,
        table_name_upper,
        name_upper,
        datatype_w_size,
        table_num,
        prev_database_base_upper,
        prev_table_name_upper,
        prev_column_name,
        prev_datatype_w_size):
    this_object_nm = f'{name_upper} {datatype_w_size}'

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME,
                                table_name_upper):
        indent_info('Notice       : Passing a difference found for {0}, {1}'.format(
            G.PROJECT_NAME,
            table_name_upper))
        return  # Don't report differences for tables that have exceptions

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME,
                                table_name_upper,
                                name_upper):
        indent_info('Notice       : Passing a difference found for {0}, {1}.{2}'.format(
            G.PROJECT_NAME,
            table_name_upper,
            name_upper))

        return  # Don't report differences for columns that have exceptions.

    report_adjustable_finding(
        object_type_nm='COLUMN',
        object_nm=this_object_nm,
        normal_severity=G.RULES[G.RULE_ID].severity,
        normal_message='Datatype diff: {0}.{1}.{2}.{3}'.format(
            database_base_upper,
            table_name_upper,
            name_upper,
            datatype_w_size),
        adjusted_message='Datatype Diff {0}.{1}.{2}.{3} accepted in ruleset {4}.'.format(
            database_base_upper,
            table_name_upper,
            name_upper,
            datatype_w_size,
            G.TABLE_STRUCTURES[int(table_num)].ruleset),
        class_object=G.TABLE_STRUCTURES[int(table_num)])

    G.LOGGER.warning((' ' * 15) + '               ' +
                     'Col unmatched: {0}.{1}.{2}.{3}'.format(
                         prev_database_base_upper,
                         prev_table_name_upper,
                         prev_column_name,
                         prev_datatype_w_size))


# ===============================================================================
def check_r299_datatype_xref(datatype_xref):
    # Sort it by column name.  Report if two consecutive lines have the same
    # column name, but different datatype_w_sizes.

    prev_database_base_upper = ''
    prev_table_name_upper = ''
    prev_column_name = ''
    prev_datatype_w_size = ''
    prev_table_num = 0
    num_findings = 0

    for line in sorted(datatype_xref):

        (column_name, datatype_w_size, source) = line.split('|')
        (database_base_upper, table_name_upper, name_upper, table_num) = source.split(':')

        if column_name == prev_column_name:
            if datatype_w_size == 'None':
                pass
            elif prev_datatype_w_size == 'None':
                pass
            elif datatype_w_size != prev_datatype_w_size:

                num_findings += 1

                if G.TABLE_STRUCTURES[int(prev_table_num)].ruleset == 'TECHDEBT' and \
                        G.TABLE_STRUCTURES[int(table_num)].ruleset != 'TECHDEBT':
                    # Give priority to the ruleset used by the previous one.
                    check_r299_report(prev_database_base_upper,
                                      prev_table_name_upper,
                                      name_upper,
                                      prev_datatype_w_size,
                                      prev_table_num,
                                      database_base_upper,
                                      table_name_upper,
                                      column_name,
                                      datatype_w_size)
                else:
                    check_r299_report(database_base_upper,
                                      table_name_upper,
                                      name_upper,
                                      datatype_w_size,
                                      table_num,
                                      prev_database_base_upper,
                                      prev_table_name_upper,
                                      prev_column_name,
                                      prev_datatype_w_size)

        prev_database_base_upper = database_base_upper
        prev_table_name_upper = table_name_upper
        prev_column_name = column_name
        prev_datatype_w_size = datatype_w_size
        prev_table_num = table_num

    return num_findings


# ===============================================================================
def check_r299():
    """
    This function checks that each column name used a consistent datatype_w_size
    and attribute.

    """

    G.RULE_ID = 'r299'

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    datatype_xref = []

    table_num = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        for G.COLUMN_ELEMENT in G.TABLE_STRUCTURE.column_elements:
            source = '{0}:{1}:{2}:{3}'.format(
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_ELEMENT.name_upper,
                table_num)

            key = '{0}|{1}'.format(
                G.COLUMN_ELEMENT.name_upper,
                G.COLUMN_ELEMENT.datatype_w_size)

            pair = '{0}|{1}'.format(key, source)

            datatype_xref.append(pair)
        table_num += 1

    # -----------------------------------------------------------------------
    # At this point, the datatype_xref list holds every datatype_w_size from
    # every column of every table.

    num_findings = check_r299_datatype_xref(datatype_xref)

    if num_findings > 1:
        indent_info('Notice       : Found {0} mismatched column datatypes.'.format(num_findings))
    elif num_findings == 1:
        indent_info('Notice       : Found {0} mismatched column datatype.'.format(num_findings))
    elif G.VERBOSE:
        indent_debug('Good         : Found no mismatched column datatypes.')

    return 0
