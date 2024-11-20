import un_re.KNOWN_DB as A
import un_re.global_shared_variables as G


# ===============================================================================
def set_database_num():
    '''
    We only cross-reference the database number to the list of Known DBs
    for TERADATA SQL
    '''

    if G.RULES_ENGINE_TYPE not in ('TERADATA_DDL', 'TERADATA_DML', 'DAMODRE'):
        G.DATABASE_NUM = -1
        return 0

    for i, known_db in enumerate(A.KNOWN_DB):
        if G.DATABASE_BASE == known_db.database_base:
            G.DATABASE_NUM = i
            G.VIEW_DATABASE_BASE = known_db.view_database_base
            break

    return 0
