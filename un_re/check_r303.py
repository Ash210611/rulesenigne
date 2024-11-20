# pylint: disable=C0209           # Don't require formtted strings
# pylint: disable=R0912				# Too many branches

import re
from bisect import bisect_left
from datetime import datetime

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.check_for_rule_exception import check_for_rule_exception
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_adjustable_finding


# ===============================================================================
# LPON
# Logical to Physical object name generation
# 1.	Work product: API to take an input variable of a logical object name, 
# 		and return as output the correct physical name (abbreviation)
# 2.	The source of the valid abbreviation list is a file maintained by 
# 		ECSM/DMCoP.
# 
# 	a.	Initially, this will not be an automated refresh.  Probably 
# 		Bev/Alan will have to manually update the list once per week.
# 
# 3.	Abbreviation algorithm:
# 	a.	The largest match of tokens between the logical title and the 
# 		abbreviation list is considered first.
# 
# 	b.	Individual tokens are translated 1:1 when no more multi-token 
# 		matches are found.
# 
# 	c.	There is a VB script that will be made available to Steve Cable
# 		for writing his own Python code.
# 
# 4.	If a token is longer than char(5) and has no abbreviation match:
# 	a.	The token fails, and the remediation is an application to the 
# 		DMCoP Kanban for a new abbreviation.
# 
# 	b.	Initially the failures could be a warning before they become 
# 		errors.
# 
# 	c.	This process is only run for Enterprise or TechDebt rule sets – 
# 		other rule sets are info-only results.
# 
# ===============================================================================
def add_token(token_num, augend, addend):
    if token_num > 0:
        augend += '_'

    augend += addend

    return augend


# ===============================================================================
def find_abbr(abbr_list, k):
    '''
    Return first single-token abbreviation with a key == k.
    Return None if not found.
    Adapted from: https://code.activestate.com/recipes/577197-sortedcollection/
    '''

    i = bisect_left(abbr_list, k)
    if i != len(abbr_list) and abbr_list[i] == k:
        return abbr_list[i]
    return None


# ===============================================================================
def replace_single_tokens(token_list):
    # print ('Replacing tokens in {0}'.format (token_list))
    derived_name = ''

    for token_num, token in enumerate(token_list):

        compare_token = C.AbbreviatedSingleToken(token, '')

        found_abbr = find_abbr(G.ABBREVIATED_SINGLE_TOKENS, compare_token)

        if found_abbr is not None:
            derived_name = add_token(
                token_num,
                derived_name,
                found_abbr.abbr.upper())
        else:
            # It is not found.
            if len(token) <= 5:
                # then this token can be accepted without
                # abbreviation
                derived_name = add_token(
                    token_num,
                    derived_name,
                    token.upper())

            else:
                # Append the unchanged lowercase token rather
                # than the matched abbreviation, to indicate
                # it has not been accepted
                derived_name = add_token(
                    token_num,
                    derived_name,
                    token)

    return derived_name


# ===============================================================================
def replace_multi_tokens(derived_name):
    # ======================================================================
    # Replace the multi-token strings first.
    while derived_name.find(' ') > -1:
        derived_name_len = len(derived_name)
        this_abbreviation = None  # initialize for pylint

        for this_abbreviation in G.ABBREVIATED_MULTI_TOKENS:
            # The abbreviations are sorted in descending length

            if this_abbreviation.phrase_len > derived_name_len:
                continue
            # The abbreviation wouldn't fit, so skip
            # until you reach an abbreviation that would
            # fit inside the derived name.

            # if not this_abbreviation.isa_multi_token_abbreviation:
            #	continue

            # if this_abbreviation.phrase_len <= 5:
            # 	# No need to check for more multi-token strings
            #	break

            if re.search(this_abbreviation.search_phrase, derived_name):

                if G.VERBOSE:
                    indent_debug('Notice-{0}  : Abbreviating {1} with {2}'.format(
                        G.RULE_ID,
                        this_abbreviation.phrase,
                        this_abbreviation.abbreviated_phrase))
                derived_name = derived_name.replace(
                    this_abbreviation.phrase,
                    this_abbreviation.abbreviated_phrase)
                break
            # See if there are any space left in the working name

        if this_abbreviation.phrase_len <= 5:
            break
        # We don't need to abbreviate anything smaller than 6 characters.

    return derived_name


# ===============================================================================
def derive_physical_name_from_logical(logical_title):
    '''
    Look up the full string in the naming file
    If found, done and return the result
    '''

    logical_title = logical_title.replace('_', ' ')
    # Logical titles should not have underscores in them.

    derived_name = logical_title.lower()  # to start with

    derived_name = replace_multi_tokens(derived_name)

    # =======================================================================
    # Now replace the single tokens, including ones <= 5 characters

    token_list = derived_name.split(' ')

    derived_name = replace_single_tokens(token_list)

    return derived_name


# ===============================================================================
def check_r303_for_1_column():
    found_an_issue = False

    if G.COLUMN_ELEMENT.title is None:
        if G.VERBOSE:
            indent_debug('Notice-{0}  : {1}.{2}.{3} has no column title.'.format(
                G.RULE_ID,
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_ELEMENT.name_upper))

    elif len(G.COLUMN_ELEMENT.title) == 0:
        if G.VERBOSE:
            indent_debug('Notice-{0}  : {1}.{2}.{3} has an empty column title.'.format(
                G.RULE_ID,
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper,
                G.COLUMN_ELEMENT.name_upper))

    else:
        if G.VERBOSE:
            G.LOGGER.debug('')
            indent_debug('Notice-{0}  : Logical title: {1}'.format(
                G.RULE_ID,
                G.COLUMN_ELEMENT.title))

        recommendation = derive_physical_name_from_logical(G.COLUMN_ELEMENT.title)

        indent_debug("Notice-{0}  : Recom'ded nm : {1}".format(
            G.RULE_ID,
            recommendation))

        if any(filter(str.islower, recommendation)):
            # If the recommendation still contains any lower
            # case chars, the abbreviation is incomplete.

            found_an_issue = True

            report_adjustable_finding(
                object_type_nm='COLUMN NAME',
                object_nm=G.COLUMN_ELEMENT.name_upper,
                normal_severity=G.RULES[G.RULE_ID].severity,
                normal_message='{0}.{1}.{2} One or more logical tokens could not be abbreviated'.format(
                    G.TABLE_STRUCTURE.database_base_upper,
                    G.TABLE_STRUCTURE.table_name_upper,
                    G.COLUMN_ELEMENT.name_upper),
                adjusted_message='Accepting one or more unfound logical tokens under ruleset {0}'.format(
                    G.TABLE_STRUCTURE.ruleset),
                class_object=G.TABLE_STRUCTURE)

        elif G.COLUMN_ELEMENT.name_upper == recommendation:
            # If the recommendation is successfully abbreviated
            # it will all be uppercase at this point.

            indent_debug((' ' * 15) + \
                         'Good         : {0}.{1}.{2} Logical title corresponds.'.format(
                             G.TABLE_STRUCTURE.database_base_upper,
                             G.TABLE_STRUCTURE.table_name_upper,
                             G.COLUMN_ELEMENT.name_upper))

        else:
            found_an_issue = True

            report_adjustable_finding(
                object_type_nm='COLUMN NAME',
                object_nm=G.COLUMN_ELEMENT.name_upper,
                normal_severity=G.RULES[G.RULE_ID].severity,
                normal_message='{0}.{1}.{2} Logical title does not correspond.'.format(
                    G.TABLE_STRUCTURE.database_base_upper,
                    G.TABLE_STRUCTURE.table_name_upper,
                    G.COLUMN_ELEMENT.name_upper),
                adjusted_message='{0}.{1}.{2} Accepting mismatched physical name under ruleset {3}'.format(
                    G.TABLE_STRUCTURE.database_base_upper,
                    G.TABLE_STRUCTURE.table_name_upper,
                    G.COLUMN_ELEMENT.name_upper,
                    G.TABLE_STRUCTURE.ruleset),
                class_object=G.TABLE_STRUCTURE)

    return found_an_issue


# ===============================================================================
def check_r303_for_1_table():
    num_columns_with_issues = 0

    if G.TABLE_STRUCTURE.database_base_upper == 'VOLATILE':
        # Columns in a volatile table would not need titles
        return num_columns_with_issues  # == return 0

    G.COLUMN_ELEMENTS = G.TABLE_STRUCTURE.column_elements

    for G.COLUMN_ELEMENT in G.COLUMN_ELEMENTS:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper, G.COLUMN_ELEMENT.name_upper):
            continue

        if check_r303_for_1_column():
            num_columns_with_issues += 1

    return num_columns_with_issues


# ===============================================================================
def check_r303():
    """
    This function checks that the logical column name (from the TITLE
    attribute) matches the physical column name
    """

    G.RULE_ID = 'r303'

    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return 0

    if len(G.ENTERPRISE_NAMING_STANDARD) == 0:
        # If the DMV database is offline, there are no abbreviations
        # available to check this, and this should be skipped.
        return 0

    if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME):
        return 0

    t1 = datetime.now()
    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_tables_with_issues = 0
    for G.TABLE_STRUCTURE in G.TABLE_STRUCTURES:

        if check_for_rule_exception(G.RULE_ID, G.PROJECT_NAME,
                                    G.TABLE_STRUCTURE.table_name_upper):
            continue

        if G.TABLE_STRUCTURE.table_name_tokens[0].upper() in ('W', 'TEMP', 'TMP'):
            # Skip this rule for work tables.
            indent_debug('Notice-{0}  : Skipped {1}.{2} for a Work table.'.format(
                G.RULE_ID,
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper))

            continue

        if G.TABLE_STRUCTURE.table_name_tokens[0].upper() == 'NC':
            # Skip this rule for NC tables.
            indent_debug('Notice-{0}  : Skipped {1}.{2} for a Non-Conformed table.'.format(
                G.RULE_ID,
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper))

            continue

        if G.TABLE_STRUCTURE.database_base_upper.find('LZ') > -1:
            indent_debug('Notice-{0}  : Skipped {1}.{2} for a Landing Zone table.'.format(
                G.RULE_ID,
                G.TABLE_STRUCTURE.database_base_upper,
                G.TABLE_STRUCTURE.table_name_upper))
            continue

        if check_r303_for_1_table() > 0:
            num_tables_with_issues += 1

    if num_tables_with_issues > 1:
        indent_info(
            'Notice-{0}  : Found {1} tables with logical naming issues.'.format(G.RULE_ID, num_tables_with_issues))
    elif num_tables_with_issues == 1:
        indent_info(
            'Notice-{0}  : Found {1} table with logical naming issues.'.format(G.RULE_ID, num_tables_with_issues))
    elif G.VERBOSE:
        indent_debug('Good         : Found no tables with logical naming issues.')

    if G.VERBOSE:
        t2 = datetime.now()
        elapsed_time = t2 - t1
        indent_debug("Notice       : Elapsed sec's: {0:d}".format(
            1 + int(elapsed_time.total_seconds())))
    return 0
