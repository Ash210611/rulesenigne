# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r702_for_1_esp_job():
    '''
    Every ESP job must specify an APPL name.
    '''

    found_an_issue = False

    if G.ESP_JOB.applid == '':
        found_an_issue = True
        report_firm_finding(
            object_type_nm='ESP APPLID',
            object_nm=G.ESP_JOB.file_basename,
            severity=G.RULES[G.RULE_ID].severity,
            message='ESP file {0} Appl name was not set.'.format(
                G.ESP_JOB.file_basename),
            class_object=G.ESP_JOB)

    elif G.ESP_JOB.file_basename != G.ESP_JOB.applid:
        found_an_issue = True
        report_firm_finding(
            object_type_nm='ESP APPLID',
            object_nm=G.ESP_JOB.file_basename,
            severity=G.RULES[G.RULE_ID].severity,
            message='ESP filename {0} does not match the Appl name {1}.'.format(
                G.ESP_JOB.file_basename,
                G.ESP_JOB.applid),
            class_object=G.ESP_JOB)

    elif G.VERBOSE:
        indent_debug('Good         : ESP file {0} has set APPL name {1}.'.format(
            G.ESP_JOB.file_basename,
            G.ESP_JOB.applid))

    return found_an_issue


# ===============================================================================
def check_r702():
    G.RULE_ID = 'r702'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r702_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP files have not set their APPLIDs.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP file has not set the APPLID.')

    elif G.VERBOSE:
        indent('Good         : All ESP files have set their APPLIDs.')
