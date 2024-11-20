# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.binary_search import binary_search
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r704_for_1_esp_job():
    found_an_issue = False

    # print (G.ESP_JOB)

    found_valid_BUC_code = binary_search(G.VALID_BUC_CODE_LIST, G.ESP_JOB.BUC_code)

    if not found_valid_BUC_code:
        found_an_issue = True
        report_firm_finding(
            object_type_nm='ESP BUC$ code',
            object_nm=G.ESP_JOB.file_basename,
            severity=G.RULES[G.RULE_ID].severity,
            message='ESP file {0} BUC$ code {1} is not valid.'.format(
                G.ESP_JOB.file_basename,
                G.ESP_JOB.BUC_code),
            class_object=G.ESP_JOB)

    elif G.VERBOSE:
        indent_debug('Good         : ESP file {0} BUC$ code {1} is valid.'.format(
            G.ESP_JOB.file_basename,
            G.ESP_JOB.BUC_code))

    return found_an_issue


# ===============================================================================
def check_r704():
    '''
    The BUC$ code must be on the approved list.
    '''

    G.RULE_ID = 'r704'

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

        if check_r704_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_applids > 0:
        if num_esp_jobs_w_findings > 1:
            indent_info('Notice       : {0} ESP files have an invalid BUC$ code.'.format(
                num_esp_jobs_w_findings))

        elif num_esp_jobs_w_findings == 1:
            indent_info('Notice       : 1 ESP file has an invalid BUC$ code.')

        elif G.VERBOSE:
            indent('Good         : All ESP files have a valid BUC$ code.')

    elif G.VERBOSE:
        indent('Notice       : No ESP files have BUC$ codes to check')
