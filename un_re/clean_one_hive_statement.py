import re


# import  un_re.global_shared_variables                as G

# ===============================================================================
def clean_one_hive_statement(sql_statement):
    '''
    This function will clean the input sql statement by replacing local
    variables with placeholders that will satisfy the SQL grammar.
    '''

    # print (sql_statement)

    # Change ${hiveconf:STG_DB}.ETL_LOAD_CYC_HADOOP_D
    # To     SomeDB.ETL_LOAD_CYC_HADOOP_D
    regex1 = r'\${.[^}]*?}\.'
    new_statement = re.sub(regex1, 'SomeDB.', sql_statement)
    if new_statement != sql_statement:
        sql_statement = new_statement
    # if G.VERBOSE:
    # 	G.LOGGER.debug ('Replaced {0} with SomeDB.'.format (regex1))
    #	print (sql_statement)

    # Change CCW_VIEW_${hivevar:env}_CLIENT_BEN_PHRM_OPT
    # To     CCW_VIEW_env_CLIENT_BEN_PHRM_OPT
    regex3 = re.compile(r'\${(.*?):(.*?)}')
    new_statement = regex3.sub(r'\2', sql_statement)
    # \2 refers to the second capture group in parentheses.
    if new_statement != sql_statement:
        sql_statement = new_statement
    # if G.VERBOSE:
    #	G.LOGGER.debug ('Replaced {0} with Colon_var.'.format (regex3))
    #	print (sql_statement)

    # Remove dollar-curly's, which start some temporary variables
    # Change ${snapshot_log}
    # To	 snapshot_log
    regex4 = re.compile(r'\${(.*?)}')
    new_statement = regex4.sub(r'\1', sql_statement)
    # \1 refers to the first capture group in parentheses.
    if new_statement != sql_statement:
        sql_statement = new_statement
    # if G.VERBOSE:
    #	G.LOGGER.debug ('Replaced {0} with Curly_var.'.format (regex4))
    #	print (sql_statement)

    # Change USE ${hiveconf:STG_DB};
    # To     USE SomeDB;
    # Given the previous regex, do we still need this?
    regex2 = re.compile(r'\${.*};')
    sql_statement = regex2.sub('SomeDB;', sql_statement)

    # Remove curly-dots, which start some temporary variables
    # Change {outbound_db}.Tablename
    # To	 outbound_db.Tablename
    regex5 = re.compile(r'{(.*?)}\.')
    new_statement = regex5.sub(r'\1.', sql_statement)
    # \1 refers to the first capture group in parentheses.
    if new_statement != sql_statement:
        sql_statement = new_statement
    # if G.VERBOSE:
    #	G.LOGGER.debug ('Replaced {0} with Curly_var.'.format (regex4))
    #	print (sql_statement)

    # Remove curly brackets, which delimit some temporary variables
    # regex5 = re.compile ( '({|})' )
    # sql_statement = regex5.sub( '', sql_statement)

    # Replace @ DatabaseName-dot variables
    # Change @hctaschema@.upd_hcta_intgrd_clm_admsn_ccw
    # To     SomeDB.upd_hcta_intgrd_clm_admsn_ccw
    regex6 = re.compile(r'@.*@\.')
    sql_statement = regex6.sub('SomeDB.', sql_statement)

    # Replace @ dot-TableName variables
    # Change SomeDB.@clm_ln_med_mv@
    # To     SomeDB.Something
    regex7 = re.compile(r'\.@.*@')
    sql_statement = regex7.sub('.Something', sql_statement)

    # Replace @ TableName-space variables
    # Change @clm_ln_med_mv@ clm
    # To     Something clm
    # regex8 = re.compile ( '@.*@ ' )
    # sql_statement = regex8.sub( '', sql_statement)

    # Also replace the angle-bracket variables
    regex = r'<.*>\.'
    compiled_regex9 = re.compile(regex)
    new_statement = compiled_regex9.sub('SomeDB.', sql_statement)
    if new_statement != sql_statement:
        sql_statement = new_statement
    # if G.VERBOSE:
    # 	G.LOGGER.debug ('Replaced {0} with SomeDB.'.format (regex))

    regex = r'_<.*>_'
    compiled_regex10 = re.compile(regex)
    new_statement = compiled_regex10.sub('Something', sql_statement)
    if new_statement != sql_statement:
        sql_statement = new_statement
    # if G.VERBOSE:
    # 	G.LOGGER.debug ('Replaced {0} with Something.'.format (regex))

    # Replace square-bracket variables
    # Change hcpm_inbound.hcpm[ENV]03_portico_PV_ENTITY_ENTITIES
    # To     hcpm_inbound.hcpm_SOMETHING_03_portico_PV_ENTITY_ENTITIES

    # Careful.
    # HIVE has a split function that can use an array index like this:
    # SELECT SPLIT(CLM_SURCHARGE_DETAIL_ID,'\\*')[0] AS SURCHARGE_CLM_ID, ...

    # The Developers will use more than simple digits in the array index.
    # They will use other database columns there.   They will use other
    # function calls there.   For those reasons, it is not feasible to
    # accurtely substitute square-bracket variables.
    # regex = r'\[\D*?\]'
    # compiled_regex11 = re.compile (regex)
    # new_statement = compiled_regex11.sub ('_SOMETHING_', sql_statement)
    # if new_statement != sql_statement:
    # sql_statement = new_statement
    # if G.VERBOSE:
    #	G.LOGGER.debug ('Replaced {0} with Something.'.format (regex))

    return sql_statement
