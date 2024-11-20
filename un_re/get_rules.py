# pylint: disable=C0209			# Don't require formatted strings.
import os
import sys
from typing import Dict

import un_re.ERROR_NUMBERS as E
import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.print_msg import print_msg


# ===============================================================================
def get_rule_for_type(rule_id, severity):
    '''
    We only need to notice the severities that are ERROR and WARNINGS.
    '''

    if severity in ('ERROR', 'WARNING'):
        G.SHOULD_CHECK_RULE[rule_id] = True

        rule = C.Rule(rule_id, severity)
        G.RULES[rule_id] = rule

        return 1

    if severity in ('TBD', 'NA'):
        return 0

    print_msg('Invalid rule severity: {0}'.format(severity))
    sys.exit(E.INVALID_SEVERITY)


# ===============================================================================
def get_rules_specific():
    """
    For now this is reading from a static table.

    A Typical rule record looks like this:

    # rule |
    # id   | ESP     | short_desc
    # -----+---------+----------+---------+---------+---------+-------------
    g001   | ERROR   | Input files must be ...

    """

    G.SHOULD_CHECK_RULE: Dict[str, bool] = {}
    G.RULES: Dict[str, C.Rule] = {}

    if G.ALTERNATIVE_RULES_LIST is None:
        rules_filenames = {}
        rules_filenames['DAMODRE'] = '/un_re/resources/rules.DAMODRE.lst'
        rules_filenames['DATA_MODEL'] = '/un_re/resources/rules.DATA_MODEL.lst'
        rules_filenames['ESP_RE'] = '/un_re/resources/rules.ESP_RE.lst'
        rules_filenames['HIVE_DDL_RE'] = '/un_re/resources/rules.HIVE_DDL_RE.lst'
        rules_filenames['PG_RE'] = '/un_re/resources/rules.PG_RE.lst'
        rules_filenames['REDSHIFT'] = '/un_re/resources/rules.REDSHIFT.lst'
        rules_filenames['TERADATA_DDL'] = '/un_re/resources/rules.TERADATA_DDL.lst'
        rules_filenames['TERADATA_DML'] = '/un_re/resources/rules.TERADATA_DML.lst'
        rules_filenames['SNOWFLAKE'] = '/un_re/resources/rules.SNOWFLAKE.lst'
        rules_filenames['DATABRICKS'] = '/un_re/resources/rules.DATABRICKS.lst'
        rules_filenames['ORE'] = '/un_re/resources/rules.ORE.lst'
        rules_filenames['DB2_RE'] = '/un_re/resources/rules.DB2_RE.lst'
        rules_filenames['DATAOPS_TDV_DDL'] = '/un_re/resources/rules.DATAOPS_TDV_DDL.lst'

        rules_filename = G.SCRIPT_DIR + rules_filenames[G.RULES_ENGINE_TYPE]
    else:

        if not os.path.exists(G.ALTERNATIVE_RULES_LIST):
            G.LOGGER.error('Error   : Alternative Rules List is not found.')
            G.LOGGER.error(f'Tried to find {G.ALTERNATIVE_RULES_LIST}')
            sys.exit(E.FILE_NOT_FOUND)

        rules_filename = G.ALTERNATIVE_RULES_LIST

    num_rules = 0

    with open(rules_filename, 'r', encoding='utf-8') as rules_file:
        for line in rules_file.readlines():

            if line.find(r'#') > -1:
                continue

            (rule_id,
             severity,
             short_desc) = line.split('|')

            rule_id = rule_id.strip()
            severity = severity.strip()

            if short_desc is None:
                print_msg('Please provide a short description for {0}'.format(
                    rule_id))
                sys.exit(E.VARIABLE_NOT_FOUND)

            if rule_id in G.AVAILABLE_RULES_TO_CHECK:
                num_rules += get_rule_for_type(rule_id, severity)

    if G.VERBOSE:
        indent('Read {0:5,d} rules.'.format(num_rules))


# ===============================================================================
def get_list_of_available_rules():
    '''
    For now this is reading from a static table.

    A Typical rule record looks like this:

    # rule |                |
    # id   | rule_ty_txt    | short_desc
    # -----+----------+---------+----------------+------------------------
    g001   | GENERAL        | Input files must be ...

    '''

    G.AVAILABLE_RULES_TO_CHECK: Dict[str, bool] = {}
    rules_filename = G.SCRIPT_DIR + '/un_re/resources/rules.lst'

    with open(rules_filename, 'r', encoding='utf-8') as rules_file:
        for line in rules_file.readlines():

            if line.find(r'#') > -1:
                continue

            # Read rule_id, rule_ty_txt, short_desc
            (rule_id, _, _) = line.split('|')

            rule_id = rule_id.strip()

            if rule_id in G.RULES_TO_SKIP:
                G.LOGGER.info(f'Pipeline will skip rule {rule_id}')
            else:
                G.AVAILABLE_RULES_TO_CHECK[rule_id] = True

    if G.VERBOSE:
        num_rules = len(G.AVAILABLE_RULES_TO_CHECK)

        indent('Read {0:5,d} available rules.'.format(num_rules))


# ===============================================================================
def get_rules():
    get_list_of_available_rules()

    if G.RULES_ENGINE_TYPE in (
            'DAMODRE', 'DATA_MODEL', 'ESP_RE', 'HIVE_DDL_RE', 'ORE',
            'DB2_RE', 'PG_RE', 'DATABRICKS', 'SNOWFLAKE', 'REDSHIFT',
            'TERADATA_DML', 'TERADATA_DDL', 'DATAOPS_TDV_DDL'):

        get_rules_specific()

    else:
        print_msg('{0}: Unknown RULES_ENGINE_TYPE: {1}'.format(
            os.path.basename(__file__),
            G.RULES_ENGINE_TYPE))
        sys.exit(E.UNKNOWN_RULES_ENGINE_TYPE)
