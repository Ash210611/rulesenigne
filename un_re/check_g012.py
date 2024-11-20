# pylint: disable=C0209			# Don't require formatted strings.

import re

import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.print_msg import report_firm_finding


# ===============================================================================
def report_techdebt_usage(line, ruleset, user_story_id):
    if user_story_id == 'NONE':

        G.RULE_ID = 'g012'
        report_firm_finding(
            object_type_nm='FILE',
            object_nm=G.INPUT_FILENAME_REL,
            severity='ERROR',
            message='The TechDebt Ruleset must be accompanied by a User Story.',
            class_object=G.INPUT_FILES[G.FILE_NUM])
        indent((' ' * 15) + f'Only found: {line}')

    else:
        G.RULE_ID = 'g013'
        if G.RULE_ID in G.SHOULD_CHECK_RULE:
            report_firm_finding(
                object_type_nm='FILE',
                object_nm=G.INPUT_FILENAME_REL,
                severity='WARNING',
                message='Ruleset indicator {0} was specified, for story: {1}.'.format(
                    ruleset,
                    user_story_id),
                class_object=G.INPUT_FILES[G.FILE_NUM])


# ===============================================================================
def classify_ruleset_indicator(line, indicator, user_story_id):
    ruleset = ''

    if re.search('TECHDEBT', indicator, re.IGNORECASE):
        ruleset = 'TECHDEBT'

        report_techdebt_usage(line, ruleset, user_story_id)

    elif re.search('ENTERPRISE', indicator, re.IGNORECASE):
        ruleset = 'ENTERPRISE'
        G.LOGGER.info('Notice-g012  : Ruleset indicator {0} was specified.'.format(
            ruleset))

    elif re.search('EXTERNALPARTY', indicator, re.IGNORECASE):
        ruleset = 'EXTERNALPARTY'
        G.LOGGER.info('Notice-g012  : Ruleset indicator {0} was specified.'.format(
            ruleset))

    elif re.search('LANDINGZONE', indicator, re.IGNORECASE):
        ruleset = 'LANDINGZONE'
        G.LOGGER.info('Notice-g012  : Ruleset indicator {0} was specified.'.format(
            ruleset))

    elif len(indicator) == 0:
        report_firm_finding(
            object_type_nm='FILE',
            object_nm=G.INPUT_FILENAME,
            severity='ERROR',
            message='An empty Ruleset indicator was specified.',
            class_object=G.INPUT_FILES[G.FILE_NUM])

    else:
        report_firm_finding(
            object_type_nm='FILE',
            object_nm=G.INPUT_FILENAME,
            severity='ERROR',
            message='An invalid Ruleset indicator was specified: {0}.'.format(
                indicator),
            class_object=G.INPUT_FILES[G.FILE_NUM])

        indent((' ' * 15) + 'Did not recognize: {0}'.format(line))

    return ruleset


# ===============================================================================
def check_g012(input_filename=None):
    G.RULE_ID = 'g012'

    # -----------------------------------------------------------------------
    if input_filename is None:
        # This rule is being called from check_all_rules(), which checks
        # individual objects rather than the whole file.

        # The process_files function will specify the file when for this
        # is right for this to be checked.
        return

    # -----------------------------------------------------------------------
    # Check the rule now that the prerequisites are passed.
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    user_story_id = 'NONE'
    ruleset = 'ENTERPRISE'

    with open(input_filename, 'r', encoding='utf-8') as in_file:
        for line in in_file.readlines():
            line = line.strip()
            if re.search(r'Ruleset\s*:', line, re.IGNORECASE):
                indicator = line.split(':', 1)[1]
                # Remove the closing block-comment symbol if present
                indicator = indicator.replace(r'*/', '')
                indicator = indicator.strip()

                if re.search('TECHDEBT', indicator, re.IGNORECASE):
                    if re.search('UserStory', line, re.IGNORECASE):
                        if line.count(':') == 2:
                            qualifier = line.split(':', 2)[2]
                            qualifier = qualifier.replace(r'*/', '')
                            qualifier = qualifier.strip()
                            user_story_id = qualifier

                ruleset = classify_ruleset_indicator(line, indicator, user_story_id)
                break

    G.INPUT_FILES[G.FILE_NUM].ruleset = ruleset
    G.INPUT_FILES[G.FILE_NUM].user_story_id = user_story_id
