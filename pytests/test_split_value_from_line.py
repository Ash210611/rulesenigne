#
# Run this Unit Test from the parent/project directory using this command:
#       python -B -m pytest pytests/test_split_value_from_line.py
#
# The split_value_from_line function is handy when reading Antlr log files,
# which reports it's observations a key-value pairs, separated by a colon,
# for example:
#	Found database identifier    : VOLATILE
#	Found relation source        : Some_DB.TMP_CLM_LN_MED_MV_REF_ALL
#	Finished in_comparison       : CHNL_SRC_CDIN('PCLM','FCTS','PMHS','DG')
#	Statement Type               : CREATE TABLE AS SELECT
#	with_data_clause             : WITHDATA
#
# ===============================================================================

import inspect

from un_re.split_value_from_line import split_value_from_line


# ===============================================================================
def test_split_a_good_line():
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    expected_value = 'CCW_BASE_DEV'
    line = 'Found database identifier    : {0}'.format(expected_value)
    value = split_value_from_line(line)

    assert value == expected_value
    print('        Passed')


# ===============================================================================
def test_colon_not_found():
    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('    {0} Running...'.format(this_function_name))

    line = 'This line is missing a colon'
    value = split_value_from_line(line)

    assert value is not None
    assert value == 'Usage Error - Colon not found.'

    print('        Passed')
