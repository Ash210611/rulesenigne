# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r711_for_1_esp_job():
    found_an_issue = False

    found_at_least_one = False

    for _ in G.ESP_JOB.top_level_agents:
        found_at_least_one = True
        break

    if found_at_least_one:
        if G.VERBOSE:
            for top_level_agent in G.ESP_JOB.top_level_agents:
                indent_debug('Good         : ESP file {0} has set top level agent name: {1}'.format(
                    G.ESP_JOB.file_basename,
                    top_level_agent))
    else:
        for G.ESP_STEP in G.ESP_JOB.esp_step:
            if G.ESP_STEP.agentname != '':
                found_at_least_one = True

                if G.VERBOSE:
                    indent_debug('Good         : ESP file {0} step {1} set agent name: {2}'.format(
                        G.ESP_JOB.file_basename,
                        G.ESP_STEP.job_name,
                        G.ESP_STEP.agentname))

    if not found_at_least_one:
        found_an_issue = True
        report_firm_finding(
            object_type_nm='ESP AGENT',
            object_nm=G.ESP_JOB.file_basename,
            severity=G.RULES[G.RULE_ID].severity,
            message='ESP file {0} Agent name was not set.'.format(
                G.ESP_JOB.file_basename),
            class_object=G.ESP_JOB)

    return found_an_issue


# ===============================================================================
def check_r711():
    G.RULE_ID = 'r711'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r711_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP files have not set an AGENT name.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP file has not set AGENT name.')

    elif G.VERBOSE:
        indent('Good         : All ESP files have set AGENT name.')
