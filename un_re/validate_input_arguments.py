# pylint: disable=C0209			# Don't require formatted strings.

import os
import sys

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G

from un_re.print_msg import print_msg


# ======== ========= ========= ========= ========= ========= ========= ==========
def validate_input_dir():
    if G.INPUT_DIR == "Unknown":
        print('')
        print_msg("Error: Please specify the INPUT_DIR variable.")
        print('')
        sys.exit(10)

    elif len(G.INPUT_DIR) == 0:
        print('')
        print_msg("Error: The INPUT_DIR variable is empty")
        print('')
        sys.exit(11)

    elif not os.path.exists(G.INPUT_DIR):
        print('')
        print_msg("Notice: The INPUT_DIR does not exist.")
        print("               The INPUT_DIR is the directory where the input files are found under.")
        print("INPUT_DIR =" + G.INPUT_DIR + "\n")
        sys.exit(0)
    # Exit 0 because some domain components have no DDL


# ======== ========= ========= ========= ========= ========= ========= ==========
def validate_rules_engine_type():
    if G.RULES_ENGINE_TYPE in (
            'TERADATA_DDL',
            'TERADATA_DML',
            'DATAOPS_TDV_DDL',
            'HIVE_DDL_RE',
            'PG_RE',
            'DB2_RE',
            'SNOWFLAKE',
            'DATABRICKS',
            'REDSHIFT',
            'DATA_MODEL',
            'ORE',
            'DAMODRE'):

        pass

    elif G.RULES_ENGINE_TYPE == 'ESP_RE':

        if G.ESP_ENVIRONMENT == '':
            print('')
            print_msg("Notice: The ESP_ENVIRONMENT is not set.")
            sys.exit(E.VARIABLE_NOT_SET)

        elif G.ESP_JOB_NAME_LENGTH_LIMIT == 0:
            print('')
            print_msg("Notice: The ESP_JOB_NAME_LENGTH_LIMIT is not set.")
            sys.exit(E.VARIABLE_NOT_SET)

    else:
        print_msg('{0}: Unknown RULES_ENGINE_TYPE: {1}'.format(
            os.path.basename(__file__),
            G.RULES_ENGINE_TYPE))
        sys.exit(E.UNKNOWN_RULES_ENGINE_TYPE)


# ======== ========= ========= ========= ========= ========= ========= ==========
def validate_input_arguments():
    validate_input_dir()

    validate_rules_engine_type()
