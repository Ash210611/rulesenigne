# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r703_for_1_esp_job():
    '''
    Every ESP APPL name must be exactly 8 chars.
    '''

    found_an_issue = False

    appl_len = len(G.ESP_JOB.applid)

    if appl_len != 8:
        found_an_issue = True
        report_firm_finding(
            object_type_nm='ESP APPLID',
            object_nm=G.ESP_JOB.file_basename,
            severity=G.RULES[G.RULE_ID].severity,
            message='ESP file {0} Appl name {1} is {2} chars, <> 8 chars.'.format(
                G.ESP_JOB.file_basename,
                G.ESP_JOB.applid,
                appl_len),
            class_object=G.ESP_JOB)

    elif G.VERBOSE:
        indent_debug('Good         : ESP file {0} APPL {1} == 8 chars.'.format(
            G.ESP_JOB.file_basename,
            G.ESP_JOB.applid))

    return found_an_issue


# ===============================================================================
def check_r703():
    '''
    An ESP APPL name must be exactly 8 characters.
    '''

    G.RULE_ID = 'r703'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0
    num_esp_jobs_w_applids = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if G.ESP_JOB.applid == '':
            continue
        # Rule 702 will report a missing applid

        num_esp_jobs_w_applids += 1

        if check_r703_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_applids > 0:
        if num_esp_jobs_w_findings > 1:
            indent_info('Notice       : {0} ESP files have APPL names <> 8 chars.'.format(
                num_esp_jobs_w_findings))

        elif num_esp_jobs_w_findings == 1:
            indent_info('Notice       : 1 ESP file has an APPL name <> 8 chars.')

        elif G.VERBOSE:
            indent_info('Good         : All ESP APPL names == 8 chars.')

    elif G.VERBOSE:
        indent_info('Notice       : No ESP files have APPL names to check')
