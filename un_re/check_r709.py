# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G

from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r709_for_1_esp_job():
    found_an_issue = False

    for G.ESP_STEP in G.ESP_JOB.esp_step:

        if G.ESP_STEP.step_type == 'JOB':
            # Don't check simple JOB JOBs
            # Only check this for job types of LINUX_JOB, AIX_JOB, etc.
            continue

        if G.ESP_STEP.step_type == 'FILE_TRIGGER':
            continue

        if G.ESP_STEP.is_external:
            # Don't check those either.
            continue

        job_name_tokens = G.ESP_STEP.job_name.split('_')

        # print ('job_name_tokens = {0}'.format (job_name_tokens))

        if job_name_tokens[0] != 'C1' and \
                job_name_tokens[0] != 'NC':
            found_an_issue = True

            this_object_name = '{0}.{1}'.format(
                G.ESP_JOB.file_basename,
                G.ESP_STEP.job_name)

            report_firm_finding(
                object_type_nm='ESP JOB NAME PREFIX',
                object_nm=this_object_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='Job name {0} needs a different prefix'.format(
                    G.ESP_STEP.job_name),
                class_object=G.ESP_JOB)

    if not found_an_issue and G.VERBOSE:
        indent_info('Good         : ESP file {0}: All steps are using an approved prefix.'.format(
            G.ESP_JOB.file_basename))

    return found_an_issue


# ===============================================================================
def check_r709():
    '''
    Every ESP step should set the criticality (C1 or NC)
    '''

    G.RULE_ID = 'r709'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r709_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP files have one or more job names that need a different prefix.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP file has one or more job names that need a different prefix.')

    elif G.VERBOSE:
        indent_info('Good         : All ESP files use job names with an approved prefix.')
