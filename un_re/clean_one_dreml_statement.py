# import	inspect
import re

from un_re.remove_leading_blank_lines import remove_leading_blank_lines


# ===============================================================================
def dreml_sub_bracket_vars(sql_statement):
    """
    If the square-bracket variable is followed by a dot, it probably
    represents a database.  Otherwise it represents something else.

    Be sure to use ? for a lazy search to match as little as possible
    """

    regex1 = re.compile(r'\[.*?\]\.', re.MULTILINE)
    regex2 = re.compile(r'\[.*?\]', re.MULTILINE)

    sql_statement = regex1.sub('Some_DB.', sql_statement)
    sql_statement = regex2.sub('Something', sql_statement)

    return sql_statement


# ===============================================================================
def dreml_sub_curly_vars(sql_statement):
    # Remove the Python variables.

    # Replace the formatted (numbered) curly-bracket variables.
    # Like 'Select {1} from Table;'.format (parameter)
    # print (sql_statement)
    sql_statement = re.sub(r'\{[0-9]*?\}', 'Something', sql_statement)

    # Replace DB suffixes like this: DATABASE CCW_RPTVIEW_${env.id.upper};
    sql_statement = re.sub(r'\$\{env\.id\.upper\}', '_XYZ', sql_statement)

    # Replace DB qualifiers like this: ${ccw_base}. (with trailing dot)
    # We have a ? after the asterisk to change the regex from greedy to lazy.
    # The [^}] improves the laziness, to make it stop matching at the first
    # closing curly bracket.
    sql_statement = re.sub(r'\$\{[^}]*?\}\.', 'Some_DB.', sql_statement)
    sql_statement = re.sub(r'\.\$\{.*?\}', '.Something', sql_statement)

    # Remove the remaining curly variables, with punctuation, without a dollar sign
    # Suppose we have this line:
    # DELETE FROM {}.{} ALL;
    sql_statement = re.sub(r'\{.*?\}\.', 'Some_DB.', sql_statement)
    sql_statement = re.sub(r'\.\{.*\}', '.Something', sql_statement)

    # Remove the dollar-curly variables
    # Suppose for example we have a line like this:
    #         FROM ${ccw_base}.CHNL_SRC_SYS${ccw_auth_qg} ;

    # Replace remaining variable references, not necessarily punctuated, with '_X'.
    # for example: FROM ${ccw_base_qg}.CHNL_SRC_SYS${ccw_auth_qg} ;
    # We have a ? after the asterisk to change the regex from greedy to lazy.
    sql_statement = re.sub(r'\$\{.*?\}', 'A_VARIABLE', sql_statement)

    # print ('Before: {0}'.format (sql_statement))

    # Hmm.  Replacement with _X becomes ambiguous with multiple variables.
    # Let's try this:
    # sql_statement = re.sub (r'\$\{', '_', sql_statement)
    # sql_statement = re.sub (r'\}',    '',  sql_statement)
    # Good.  That changes it to _ccw_base_qg.CHNL_SRC_SYS_ccw_auth_qg,
    # which is more unique

    return sql_statement


# ===============================================================================
def dreml_sub_format_vars(sql_statement):
    '''
    For example:
        DELETE FROM %s ;
    '''

    sql_statement = re.sub(r'%s', 'Something', sql_statement)

    return sql_statement


# ===============================================================================
def clean_one_dreml_statement(sql_statement):
    # print ('Line {0}: {1}'.format (inspect.currentframe().f_lineno, sql_statement))
    sql_statement = dreml_sub_bracket_vars(sql_statement)

    sql_statement = dreml_sub_curly_vars(sql_statement)

    sql_statement = dreml_sub_format_vars(sql_statement)

    sql_statement = remove_leading_blank_lines(sql_statement)

    return sql_statement
