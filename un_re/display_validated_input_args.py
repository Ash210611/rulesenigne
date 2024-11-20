# pylint: disable=C0209           # Don't require formtted strings

import os
import sys

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G
from un_re.print_msg import print_msg


# ======== ========= ========= ========= ========= ========= ========= ==========
def display_validated_input_args():
    G.LOGGER.info('Rules Eng Typ= {0}'.format(G.RULES_ENGINE_TYPE))
    G.LOGGER.info('Load Events  = {0}'.format(G.LOAD_EVENT_RECORDS))

    if G.RULES_ENGINE_TYPE in ('TERADATA_DDL', 'DATAOPS_TDV_DDL'):
        G.LOGGER.info('')

        if G.VERBOSE:
            G.LOGGER.debug('NDTSLF       = {0}'.format(G.NUM_DAYS_TO_SAVE_LOG_FILES))

        G.LOGGER.info('')
        G.LOGGER.info('INPUT_DIR    = {0}'.format(G.INPUT_DIR))
        G.LOGGER.info('Decomment XML= {0}'.format(G.DECOMMENT_XML))
        G.LOGGER.info('PARALLEL_DEG = {0}'.format(G.PARALLEL_DEGREE))
        G.LOGGER.info('Log Level    = {0}'.format(G.LOGGER.getEffectiveLevel()))

    elif G.RULES_ENGINE_TYPE in ['HIVE_DDL_RE',
                                 'PG_RE',
                                 'DB2_RE',
                                 'DATA_MODEL',
                                 'DAMODRE',
                                 'TERADATA_DML',
                                 'ESP_RE',
                                 'SNOWFLAKE',
                                 'DATABRICKS',
                                 'ORE',
                                 'REDSHIFT']:

        G.LOGGER.info('INPUT_DIR    = {0}'.format(G.INPUT_DIR))
        G.LOGGER.info('PARALLEL_DEG = {0}'.format(G.PARALLEL_DEGREE))

    else:
        print_msg('{0}: Unknown RULES_ENGINE_TYPE: {1}'.format(
            os.path.basename(__file__),
            G.RULES_ENGINE_TYPE))
        sys.exit(E.UNKNOWN_RULES_ENGINE_TYPE)

    if G.RULES_ENGINE_TYPE == 'ESP_RE':
        G.LOGGER.info('ESP Envirmnt = {0}'.format(G.ESP_ENVIRONMENT))
        G.LOGGER.info('ESP Nm Limit = {0}'.format(G.ESP_JOB_NAME_LENGTH_LIMIT))

    if G.ALTERNATIVE_RULES_LIST is not None:
        G.LOGGER.info('Alt Rule List= {0}'.format(G.ALTERNATIVE_RULES_LIST))
