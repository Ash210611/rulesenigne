import re

from un_re.indent import indent
from un_re.print_one_sql_statement import wrap_one_sql_statement
from un_re.print_msg import print_msg


# ===============================================================================
def string_has_a_dml_statement(inp_string):
    keywords = ['CREATE',
                'COMMENT',
                'DATABASE',
                'INS',
                'INSERT',
                'SEL',
                'SELECT',
                'UPD',
                'UPDATE',
                'DEL',
                'DELETE',
                'VOLATILE'
                ]
    for keyword in keywords:
        if re.search(fr'\b{keyword}\b', inp_string, re.IGNORECASE):
            return True

    return False


# ===============================================================================
def is_a_dml_statement(sql_statement):
    '''
    If this is a Create Table command, it should be a Create Volatile
    Table command.
    It would be OK for them to create a NON-Volatile table in the ERR
    database
    '''

    if re.search(r'<html>', sql_statement, re.IGNORECASE | re.MULTILINE):
        wrap_one_sql_statement(sql_statement)
        indent('Skipped, as that appears more like HTML than a DML statement.')
        return False

    if re.search(r'CREATE.*TABLE', sql_statement, re.IGNORECASE | re.MULTILINE):

        if re.search('ERR', sql_statement, re.IGNORECASE):
            pass
        # Apparently we let people create any table they want
        # in the ERR database

        elif re.search(r'VOLATILE', sql_statement, re.IGNORECASE):
            pass
        # We will test Volatile tables later for being MULTISET

        else:
            wrap_one_sql_statement(sql_statement)
            print_msg('ERROR:  If you create a table with ETL, either make it Volatile, or put it in the ERR database.')
        # This will be checked again with greater accuracy
        # by rule 510

    # \b is used to match whole words
    elif not string_has_a_dml_statement(sql_statement):

        wrap_one_sql_statement(sql_statement)
        indent('Skipped, as that does not appear to be a DML statement.')
        return False

    return True
