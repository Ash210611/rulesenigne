# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r718_for_1_esp_job():
    found_an_issue = False

    n = len(G.ESP_JOB.esp_step)
    for i in range(n):

        for j in range(i + 1, n):
            if G.ESP_JOB.esp_step[i].job_name == G.ESP_JOB.esp_step[j].job_name:
                found_an_issue = True

                this_object_nm = '{0}.{1}'.format(
                    G.ESP_JOB.file_basename,
                    G.ESP_STEP.job_name)

                report_firm_finding(
                    object_type_nm='ESP JOB ARGS',
                    object_nm=this_object_nm,
                    severity=G.RULES[G.RULE_ID].severity,
                    message='ESP step {0} is duplicated.'.format(
                        G.ESP_JOB.esp_step[i].job_name),
                    class_object=G.ESP_JOB)

    if G.VERBOSE and not found_an_issue:
        indent_debug('Good         : ESP JOB {0} has no duplicated steps.'.format(
            G.ESP_JOB.file_basename))

    return found_an_issue


# ===============================================================================
def check_r718():
    '''
    Steps names in an ESP Job must be unique.
    '''

    G.RULE_ID = 'r718'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r718_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP Jobs have duplicate step names.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP Job has a duplicated step name.')

    elif G.VERBOSE:
        indent('Good         : No ESP jobs have duplicated step names.')
