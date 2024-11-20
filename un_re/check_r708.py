# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G

from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r708_for_1_esp_job():
    found_an_issue = False

    step_num = 0
    for G.ESP_STEP in G.ESP_JOB.esp_step:
        step_num += 1

        if G.ESP_STEP.step_type == 'FILE_TRIGGER':
            continue

        job_name_len = len(G.ESP_STEP.job_name)

        if job_name_len > G.ESP_JOB_NAME_LENGTH_LIMIT:
            found_an_issue = True

            this_object_nm = '{0}.Step_{1}.{2}'.format(
                G.ESP_JOB.file_basename,
                step_num,
                G.ESP_STEP.job_name)

            report_firm_finding(
                object_type_nm='ESP JOB NAME',
                object_nm=this_object_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='Job {0} name is {1} bytes, >{2}.'.format(
                    G.ESP_STEP.job_name,
                    job_name_len,
                    G.ESP_JOB_NAME_LENGTH_LIMIT),
                class_object=G.ESP_JOB)

        elif job_name_len > 23:
            found_an_issue = True

            this_object_nm = '{0}.Step_{1}.{2}'.format(
                G.ESP_JOB.file_basename,
                step_num,
                G.ESP_STEP.job_name)

            report_firm_finding(
                object_type_nm='ESP JOB NAME',
                object_nm=this_object_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='Shorten job name {0} to 23 chars.'.format(
                    G.ESP_STEP.job_name),
                class_object=G.ESP_JOB)

    if not found_an_issue and G.VERBOSE:
        indent_info('Good         : ESP file {0}: All steps have job names within the length limit.'.format(
            G.ESP_JOB.file_basename))

    return found_an_issue


# ===============================================================================
def check_r708():
    G.RULE_ID = 'r708'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r708_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP files have one or more job names too long.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP file has one or more job names too long.')

    elif G.VERBOSE:
        indent_info('Good         : All ESP files use job names within the length limit.')
