# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r705_for_1_esp_job():
    found_an_issue = False

    last_byte = G.ESP_JOB.applid[-1]

    if (G.ESP_ENVIRONMENT == 'PROD' and
        last_byte != '6') or \
            (G.ESP_ENVIRONMENT != 'PROD' and
             last_byte == '6'):

        found_an_issue = True
        report_firm_finding(
            object_type_nm='ESP APPLID ENV',
            object_nm=G.ESP_JOB.file_basename,
            severity=G.RULES[G.RULE_ID].severity,
            message='Appl name {0} does not correspond to the target environment {1}.'.format(
                G.ESP_JOB.applid,
                G.ESP_ENVIRONMENT),
            class_object=G.ESP_JOB)

    elif G.VERBOSE:
        indent_debug('Good         : ESP file {0} APPL {1} corresponds to the {2} environment'.format(
            G.ESP_JOB.file_basename,
            G.ESP_JOB.applid,
            G.ESP_ENVIRONMENT))

    return found_an_issue


# ===============================================================================
def check_r705():
    '''
    If the ESP ENVIRONMENT == 'PROD', the last byte of the APPL name must = 6

    For other ESP ENVIRONMENTS, the last byte must not be 6
    '''

    G.RULE_ID = 'r705'

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

        if check_r705_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_applids > 0:
        if num_esp_jobs_w_findings > 1:
            indent_info("Notice       : {0} ESP APPL names don't correspond with the target environment.".format(
                num_esp_jobs_w_findings))

        elif num_esp_jobs_w_findings == 1:
            indent_info("Notice       : 1 ESP APPL name doesn't correspond with the target environment.")

        elif G.VERBOSE:
            indent_info('Good         : All ESP APPL names correspond with the target environment.')

    elif G.VERBOSE:
        indent_info('Notice       : No ESP files have APPL names to check')
