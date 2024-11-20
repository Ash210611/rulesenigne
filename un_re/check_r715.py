# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r715_for_1_esp_job():
    found_an_issue = False

    for G.ESP_STEP in G.ESP_JOB.esp_step:

        if (G.ESP_ENVIRONMENT == 'PROD' and
            re.search(r'(DEV|INT|PVS)', G.ESP_STEP.args, re.IGNORECASE)) or \
                (G.ESP_ENVIRONMENT != 'PROD' and
                 re.search(r'(PROD|PRD)', G.ESP_STEP.args, re.IGNORECASE)):
            found_an_issue = True

            this_object_nm = '{0}.{1}'.format(
                G.ESP_JOB.file_basename,
                G.ESP_STEP.job_name)

            report_firm_finding(
                object_type_nm='ESP JOB ARGS',
                object_nm=this_object_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='ESP step {0} has an inappropriate arg.'.format(
                    G.ESP_STEP.job_name),
                class_object=G.ESP_JOB)

            indent_info('Notice       : ARGS={0}'.format(
                G.ESP_STEP.args))

    if G.VERBOSE and not found_an_issue:
        indent_debug('Good         : ESP file {0} all steps arg using allowed args.'.format(
            G.ESP_JOB.file_basename))

    return found_an_issue


# ===============================================================================
def check_r715():
    '''
    Every ESP step must specify a script name.
    '''

    G.RULE_ID = 'r715'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r715_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP files have inappropriate args.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP file has an inappropriate arg.')

    elif G.VERBOSE:
        indent('Good         : All ESP files have allowed args.')
