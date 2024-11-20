# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r710_for_1_esp_job():
    found_an_issue = False

    for G.ESP_STEP in G.ESP_JOB.esp_step:

        buc_assoc = r'(C1|NC)_{0}'.format(G.ESP_JOB.BUC_code)
        # print ('buc_assoc = {0}'.format (buc_assoc))

        if not re.search(buc_assoc, G.ESP_STEP.job_name, re.IGNORECASE):
            found_an_issue = True

            this_object_name = '{0}.{1}'.format(
                G.ESP_JOB.file_basename,
                G.ESP_STEP.job_name)

            report_firm_finding(
                object_type_nm='ESP JOB BUC ASSOC',
                object_nm=this_object_name,
                severity=G.RULES[G.RULE_ID].severity,
                message='Job name {0} is missing a BUC association'.format(
                    G.ESP_STEP.job_name),
                class_object=G.ESP_JOB)

    if not found_an_issue and G.VERBOSE:
        indent_info('Good         : ESP file {0}: All steps have a valid BUC association.'.format(
            G.ESP_JOB.file_basename))

    return found_an_issue


# ===============================================================================
def check_r710():
    G.RULE_ID = 'r710'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r710_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP files have one or more job names with a missing BUC association.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP file has one or more job names with a missing BUC association.')

    elif G.VERBOSE:
        indent_info('Good         : All ESP files use job names valid BUC associations.')
