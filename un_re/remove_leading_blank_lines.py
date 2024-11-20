import re


# ===============================================================================
def remove_leading_blank_lines(sql_stmt_txt):
    new_lines = []

    lines = sql_stmt_txt.split('\n')

    found_txt = False
    for line in lines:
        if not found_txt:
            if not re.search(r'^$', line):
                found_txt = True
        # else that line will be skipped

        if found_txt:
            # Once we found some text, append all remaining lines
            new_lines.append(line)

    new_sql_stmt_txt = '\n'.join(new_lines)

    return new_sql_stmt_txt
