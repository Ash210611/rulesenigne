# pylint: disable=C0209			# don't require formatted strings

import configparser
import os
import sys

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.print_msg import print_msg


# ======== ========= ========= ========= ========= ========= ========= ==========
def get_1_env_value(filename, option, is_optional):
    section = "UN_RE"

    Config = configparser.ConfigParser()
    Config.read(filename)
    try:
        value = Config.get(section, option)
        return value
    except configparser.NoOptionError:
        if is_optional:
            return None

        G.LOGGER.error('')
        print_msg(f"ERROR: Variable {option} is not found")
        indent('       Variable not found in : {0}'.format(
            os.path.basename(__file__)))

        sys.exit(E.VARIABLE_NOT_FOUND)
    except:
        G.LOGGER.error('')
        print_msg("ERROR: An unknown error occured.")
        G.LOGGER.error('Error trying to read:{0}'.format(filename))
        raise
    # sys.exit (13)
