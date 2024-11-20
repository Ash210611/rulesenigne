import un_re.global_shared_variables as G

from un_re.indent_warning import indent_warning


# ===============================================================================
def antlr_show_context(log_line, filename_to_check):
    issue_line_num = log_line.split(':', 1)[0]

    try:
        issue_line_num = issue_line_num.split(' ')[1]
    except IndexError:
        G.LOGGER.warning(f'Log line has no space: {log_line}')
        return

    try:
        issue_line_num = int(issue_line_num)
    except ValueError:
        G.LOGGER.warning(f'Log line is not an integer: {log_line}')
        return

    indent_warning('Antlr Error Summary:')
    indent_warning(f'Unknown syntax near line {issue_line_num}')

    # Try to provide a line of context before and after the
    # the line with no viable alternative
    prev_line_1 = ''  # The line before this one
    prev_line_2 = ''  # The line before THAT one
    line = ''  # for pylint

    num_lines_read = 0
    with open(filename_to_check, 'r', encoding='utf-8') as inp_file:
        for line in inp_file.readlines():
            line = line.rstrip('\n')
            num_lines_read += 1
            if num_lines_read == issue_line_num + 1:
                break
            prev_line_2 = prev_line_1
            prev_line_1 = line

    # print (__file__)
    # print (f'issue_line_num = {issue_line_num}')
    # print (f'prev_line_2    = {prev_line_2}')
    # print (f'prev_line_1    = {prev_line_1}')
    # print (f'line           = {line}')
    # print (f'num_lines_read = {num_lines_read}')

    if issue_line_num > 2:
        indent_warning(prev_line_2)
    if issue_line_num > 1:
        indent_warning(prev_line_1)

    if num_lines_read == 1:
        indent_warning(line)
    elif issue_line_num <= num_lines_read - 1:
        indent_warning(line)
