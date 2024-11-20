# File: load_configuration_files.py
#
# ===============================================================================
import un_re.global_shared_variables as G

from un_re.get_bad_char_list import get_bad_char_list

from un_re.get_cfg_array_exceptions import get_cfg_array_exceptions
from un_re.get_cfg_articles import get_cfg_articles
from un_re.get_cfg_business_terms import get_cfg_business_terms
from un_re.get_cfg_classwords import get_cfg_classwords
from un_re.get_cfg_classword_datatypes import get_cfg_classword_datatypes
from un_re.get_cfg_classword_datatype_variations import get_cfg_classword_datatype_variations
from un_re.get_cfg_classword_exceptions import get_cfg_classword_exceptions
from un_re.get_cfg_Enterprise_Naming_Standards import get_cfg_Enterprise_Naming_Standards
from un_re.get_cfg_extrnl_nm import get_cfg_extrnl_nm
from un_re.get_cfg_known_db import get_cfg_known_db
from un_re.get_cfg_multiset_base_tables import get_cfg_multiset_base_tables
from un_re.get_cfg_rules_exceptions import get_cfg_rules_exceptions
from un_re.get_cfg_techdebt_exclusions import get_cfg_techdebt_exclusions

from un_re.get_expected_content import get_expected_content
from un_re.get_rules import get_rules
from un_re.get_rules_urls import get_rules_urls
from un_re.get_ruleset_severities import get_ruleset_severities
from un_re.get_valid_BUC_codes import get_valid_BUC_codes
from un_re.get_uncleared_techdebt import get_uncleared_techdebt
from un_re.classify_command_type import populate_command_regexes


# ===============================================================================
def load_configuration_files():
    get_rules()
    get_rules_urls()
    get_ruleset_severities()

    get_expected_content()

    if G.RULES_ENGINE_TYPE == 'ESP_RE':
        get_valid_BUC_codes()
    else:
        get_cfg_rules_exceptions()
        get_cfg_array_exceptions()
        get_cfg_articles()
        get_cfg_business_terms()
        get_cfg_classwords()
        get_cfg_classword_exceptions()
        get_cfg_classword_datatype_variations()
        get_cfg_classword_datatypes()
        get_cfg_techdebt_exclusions()

    if G.RULES_ENGINE_TYPE in ('TERADATA_DDL', 'TERADATA_DML', 'DATAOPS_TDV_DDL'):
        get_cfg_known_db()

    if G.RULES_ENGINE_TYPE in ('TERADATA_DDL', 'DATAOPS_TDV_DDL'):
        get_cfg_multiset_base_tables()

    if G.RULES_ENGINE_TYPE != 'ESP_RE':
        get_cfg_Enterprise_Naming_Standards()
        get_cfg_extrnl_nm()
        get_uncleared_techdebt()

    populate_command_regexes()
    get_bad_char_list()
