import re


# import  un_re.global_shared_variables    as G

# ======== ========= ========= ========= ========= ========= ========= ==========
def prepare_stmt(sql_stmt_txt):
    """
    This function will replace liquibase database variable, ${env.id.upper},
    if present, with an actual environment name, because it is
    too hard to parse database and object names if that is present.

    Will also remove the NO FALLBACK clause, because that is disallowed by
    Intelliflex.  The NO FALLBACK clause is removed by the Liquibase
    PreProcessor, LQBPP
    """

    # if G.VERBOSE:
    # 	G.LOGGER.debug ('               Preparing the SQL_STATEMENT for processing...')

    sql_stmt_txt = re.sub(r'\${env.id.upper}', '_DEV', sql_stmt_txt, flags=re.IGNORECASE)

    sql_stmt_txt = re.sub(',.*NO FALLBACK', '', sql_stmt_txt)

    sql_stmt_txt = re.sub('NO FALLBACK.*,', '', sql_stmt_txt)

    sql_stmt_txt = re.sub(r'\${TEMPLATE:.*?;', r"Select 'Noticed Template';", sql_stmt_txt)
    # Use the question mark there to change greedy matching to lazy matching.

    # if G.VERBOSE:
    #	G.LOGGER.debug ('               Done preparing the SQL_STATEMENT for processing...')

    return sql_stmt_txt
