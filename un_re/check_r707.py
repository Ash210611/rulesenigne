# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r707_for_1_esp_job():
    found_an_issue = False

    step_num = 0
    for G.ESP_STEP in G.ESP_JOB.esp_step:
        step_num += 1

        if G.ESP_STEP.step_type == 'JOB':
            # Don't check simple JOB JOBs
            # Only check this for job types of LINUX_JOB, AIX_JOB, etc.
            continue

        if G.ESP_STEP.step_type == 'FILE_TRIGGER':
            continue

        if G.ESP_STEP.is_external:
            # Don't check those either.
            continue

        if G.ESP_STEP.docmember_name == 'None':
            found_an_issue = True

            this_object_name = '{0}.Step_{1}.{2}'.format(
                G.ESP_JOB.file_basename,
                step_num,
                G.ESP_STEP.job_name)

            report_firm_finding(
                object_type_nm='ESP DOCMEM',
                object_nm=this_object_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='ESP file {0} Job {1} DOCMEM is missing.'.format(
                    G.ESP_JOB.file_basename,
                    G.ESP_STEP.job_name),

                class_object=G.ESP_JOB)

        elif not re.search(r'{0}CALL'.format(G.ESP_JOB.BUC_code), G.ESP_STEP.docmember_name):

            found_an_issue = True

            this_object_name = '{0}.Step_{1}.{2}'.format(
                G.ESP_JOB.file_basename,
                step_num,
                G.ESP_STEP.job_name)

            report_firm_finding(
                object_type_nm='ESP DOCMEM',
                object_nm=this_object_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='ESP file {0} Job {1} DOCMEM ({2}) is invalid.'.format(
                    G.ESP_JOB.file_basename,
                    G.ESP_STEP.job_name,
                    G.ESP_STEP.docmember_name),
                class_object=G.ESP_JOB)

    if not found_an_issue and G.VERBOSE:
        indent_info('Good         : ESP file {0}: All steps have a valid DOCMEM.'.format(
            G.ESP_JOB.file_basename))

    return found_an_issue


# ===============================================================================
def check_r707():
    '''
    Every ESP step should set a Doc member name
    '''

    G.RULE_ID = 'r707'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r707_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP files have a missing or invalid DOCMEM.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP file has a missing or invalid DOCMEM.')

    elif G.VERBOSE:
        indent_info('Good         : All ESP files have valid DOCMEMs.')