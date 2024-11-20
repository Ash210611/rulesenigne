# ===============================================================================
def split_value_from_line(line):
    try:
        value = line.split(':', 1)[1]
    except IndexError:
        value = 'Usage Error - Colon not found.'

    value = value.strip()

    return value
