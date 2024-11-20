# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r712_for_1_esp_job():
    found_an_issue = False

    for G.ESP_STEP in G.ESP_JOB.esp_step:
        if G.ESP_STEP.frequency == '':
            found_an_issue = True

            report_firm_finding(
                object_type_nm='ESP JOB FREQUENCY',
                object_nm=G.ESP_JOB.file_basename,
                severity=G.RULES[G.RULE_ID].severity,
                message='ESP step {0} did not set a frequency.'.format(
                    G.ESP_STEP.job_name),
                class_object=G.ESP_JOB)

    if G.VERBOSE and not found_an_issue:
        indent_debug('Good         : ESP file {0} all steps set a frequency'.format(
            G.ESP_JOB.file_basename))

    return found_an_issue


# ===============================================================================
def check_r712():
    G.RULE_ID = 'r712'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r712_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP files are missing a job schedule.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP file is missing a job schedule.')

    elif G.VERBOSE:
        indent('Good         : All ESP files are setting job schedules for all jobs.')
