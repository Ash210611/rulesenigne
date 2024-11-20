import un_re.global_shared_variables as G

from un_re.clean_database_base import clean_database_base
from un_re.indent_error import indent_error


# ===============================================================================
def split_db_from_obj_name(obj_name):
    # In this case the Create Table command
    # is using a database qualifier in the
    # command rather than a USE DATABASE command.

    G.DATABASE_BASE = obj_name.split('.')[0]

    try:
        obj_name = obj_name.split('.')[1]

    except Exception:
        indent_error(f'Cannot split object name: {obj_name}')
        raise

    G.DATABASE_BASE = clean_database_base(G.DATABASE_BASE)
    # Remove any back ticks
    # And remove the environment suffix, if any

    if G.VERBOSE:
        G.LOGGER.debug(f'Database Base: {G.DATABASE_BASE}')

    return G.DATABASE_BASE, obj_name
