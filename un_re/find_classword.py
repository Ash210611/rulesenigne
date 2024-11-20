import un_re.global_shared_variables as G

from un_re.binary_search import binary_search


# Note I would prefer this to be called automatically when the column class is
# created, but doing that creates a circular import.
# Therefore, after calling AC=C.AntlrColumn(...), you should immediated call
#	AC.classword = find_classword (...)
#
# ===============================================================================
def find_classword(naming_method, column_name_tokens):
    # print (f'naming_method: {naming_method}')
    # print (f'column_name_tokens: {column_name_tokens}')

    for column_part in reversed(column_name_tokens):
        # Take the classword most towards the end of the column name

        column_part = column_part.upper()
        if naming_method == 'SNAKE_CASE':
            if binary_search(G.PHYSICAL_CLASSWORD_LIST, column_part):
                return column_part
        elif naming_method == 'MixedCase':
            if binary_search(G.LOGICAL_CLASSWORD_LIST, column_part):
                return column_part
        elif naming_method == 'SMASHED':
            if binary_search(G.PHYSICAL_CLASSWORD_LIST, column_part):
                return column_part
            if binary_search(G.LOGICAL_CLASSWORD_LIST, column_part):
                return column_part

    # print (f'Did not find classword for column_part: {column_part}')
    # print (f'{G.PHYSICAL_CLASSWORD_LIST}')
    return None
