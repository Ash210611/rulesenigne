# pylint: disable=C0209           # Don't require formtted strings
# pylint: disable=C0301           # Allow long lines

import un_re.global_shared_variables as G


# from	un_re.indent_debug			import indent_debug
# from	un_re.print_msg				import report_firm_finding

# ===============================================================================

def check_r261():
    """
    Physical table name should be derived from Datamodel table .
    """
    G.RULE_ID = 'r261'

    # Prerequisites
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    return

# Skipping this for now.
# -----------------------------------------------------------------------
# G.LOGGER.info (f'Checking rule {G.RULE_ID}...')

# num_findings = 0
# for G.ENTITY in G.ENTITIES:
# if there is an nsmfile in the model then
#     compare table name to nsm translation of name
#     if not match then
#         check to see if name is hardened
#         if not then _retval = 'FAIL'
#                 break
#         else return 'HARDENED'
#                 break
# else return 'MISSING'
#                 break


#	if retval == 'FAIL':
# 		report_firm_finding (
#                         object_type_nm  = 'ENTITY',
#                         object_nm       = G.ENTITY.entty_nm,
#                         severity        = G.RULES[G.RULE_ID].severity,
#                         message         = '{0} was not derived from logical name: {1}'.format(G.ENTITY.tbl_nm, G.ENTITY.entty_nm),
# 			class_object	= G.ENTITY)
# 		num_findings += 1

# elif retval == 'HARDENED':
# 		report_firm_finding (
#                         object_type_nm  = 'ENTITY',
#                         object_nm       = G.ENTITY.entty_nm,
#                         severity        = 'WARNING',
#                         message         = '{0} was HARDENED and not derived from logical name: {1}'.format(G.ENTITY.tbl_nm, G.ENTITY.entty_nm),
# 				class_object	= G.ENTITY)
#		num_findings += 1

# elif retval == 'MISSING':
# 		report_firm_finding (
#                         object_type_nm  = 'ENTITY',
#                         object_nm       = G.ENTITY.entty_nm,
#                         severity        = 'WARNING',
#                         message         = '{0} was translated without NSM file into: {1}'.format(G.ENTITY.tbl_nm, G.ENTITY.entty_nm),
# 			class_object	= G.ENTITY)
# 		num_findings += 1

# 	elif G.VERBOSE:
# 		txt = G.ENTITY.entty_nm  and '...'

# 		indent_debug ('Good         : Entity:  {0} was derived from {1}'.format (
# 			G.ENTITY.tbl_nm, G.ENTITY.entty_nm))
# if num_findings == 0:
# 	if G.VERBOSE:
# 		indent_debug ('Good         : All table names were derived from entity names using NSM file.')
