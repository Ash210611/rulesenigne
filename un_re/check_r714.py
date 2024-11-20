# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r714_for_1_esp_job():
    found_an_issue = False

    for G.ESP_STEP in G.ESP_JOB.esp_step:
        # print ('step_type = {0}'.format (G.ESP_STEP.step_type))
        if G.ESP_STEP.step_type == 'JOB':
            # Don't check simple JOB JOBs
            # Only check this for job types of LINUX_JOB, AIX_JOB, etc.
            continue

        if G.ESP_STEP.step_type == 'FILE_TRIGGER':
            continue

        if G.ESP_STEP.is_external:
            # Don't check those either.
            continue

        if G.ESP_STEP.scriptname == '' and \
                G.ESP_STEP.cmdname == '':
            found_an_issue = True

            report_firm_finding(
                object_type_nm='ESP JOB SCRIPTNAME',
                object_nm=G.ESP_JOB.file_basename,
                severity=G.RULES[G.RULE_ID].severity,
                message='ESP step {0} did not set a script or command name.'.format(
                    G.ESP_STEP.job_name),
                class_object=G.ESP_JOB)

    if G.VERBOSE and not found_an_issue:
        indent_debug('Good         : ESP file {0} all steps set a script or command name.'.format(
            G.ESP_JOB.file_basename))

    return found_an_issue


# ===============================================================================
def check_r714():
    '''
    Every ESP step must specify a script name.
    '''

    G.RULE_ID = 'r714'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r714_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP files are missing a script or command name.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP file is missing a script or command name.')

    elif G.VERBOSE:
        indent('Good         : All ESP files are setting a script or command name for all jobs.')
