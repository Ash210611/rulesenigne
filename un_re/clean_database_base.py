import re

import un_re.global_shared_variables as G


# ===============================================================================
def clean_database_base(database_base):
    '''
    Remove any back ticks
        And remove the environment suffix, if any
    '''

    database_base = database_base.strip("`")

    if G.RULES_ENGINE_TYPE in (
            'TERADATA_DDL',
            'TERADATA_DML',
            'DAMODRE'):
        # Remove the environment from the database name
        # regex =  r'[2-3]*_[A-Z]{3}$'
        database_base = re.sub(r'[2-3]*_[A-Z]{3}$', '', database_base, re.IGNORECASE)

    return database_base
