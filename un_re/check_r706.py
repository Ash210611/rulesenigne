# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r706_for_1_esp_job():
    '''
    APPLSTART and APPLEND are both in the body.
    '''

    found_an_issue = False

    if not G.ESP_JOB.found_applstart:
        found_an_issue = True
        report_firm_finding(
            object_type_nm='ESP APPLSTART',
            object_nm=G.ESP_JOB.file_basename,
            severity=G.RULES[G.RULE_ID].severity,
            message='ESP filename {0} does not have an APPLSTART command.'.format(
                G.ESP_JOB.file_basename),
            class_object=G.ESP_JOB)

    if not G.ESP_JOB.found_applend:
        found_an_issue = True
        report_firm_finding(
            object_type_nm='ESP APPLEND',
            object_nm=G.ESP_JOB.file_basename,
            severity=G.RULES[G.RULE_ID].severity,
            message='ESP filename {0} does not have an APPLEND command.'.format(
                G.ESP_JOB.file_basename),
            class_object=G.ESP_JOB)

    if G.VERBOSE and not found_an_issue:
        indent_debug('Good         : ESP file {0} has an APPLSTART and APPLEND command.'.format(
            G.ESP_JOB.file_basename))

    return found_an_issue


# ===============================================================================
def check_r706():
    G.RULE_ID = 'r706'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r706_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP files did not set both APPL endpoints.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP file did not set both APPL endpoints.')

    elif G.VERBOSE:
        indent('Good         : All ESP files set both APPL endpoints.')
