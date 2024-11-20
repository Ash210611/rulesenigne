# pylint: disable=C0209			# don't require formatted strings.

import textwrap

import un_re.global_shared_variables as G

from un_re.indent_info import indent_info


# ===============================================================================
def wrap_one_sql_statement(sql_stmt_txt):
    line_num = 0
    for sql_fragment in sql_stmt_txt.split('\n'):
        line_num += 1
        line = '\n'.join(textwrap.wrap(sql_fragment, width=80, replace_whitespace=False))

        # Count the number of segments, to enable different formats
        num_segments = 0
        for _ in line.split('\n'):
            num_segments += 1

        segment_num = 0
        for line_segment in line.split('\n'):
            segment_num += 1
            line_segment = line_segment.encode('ascii', 'ignore').decode('ascii')
            # That is needed because the logger can only
            # handle ascii, even though the logger handler
            # is encoded utf-8.   Ugh.
            if num_segments == 1:
                G.LOGGER.info('        {0:4d}   {1}'.format(
                    line_num,
                    line_segment))
            else:
                G.LOGGER.info('        {0:4d}.{1:d} {2}'.format(
                    line_num,
                    segment_num,
                    line_segment))


# ===============================================================================
def print_one_sql_statement(sql_obj):
    G.LOGGER.info('')
    indent_info('-' * 72)
    G.LOGGER.info('        Line   Stmt Number  : {0}'.format(sql_obj.sql_stmt_num + 1))

    wrap_one_sql_statement(sql_obj.sql_stmt_txt)
