# pylint: disable=C0209           		# Don't require formtted strings
# pylint: disable=R0912				# Too many branches

import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r716_for_1_esp_job():
    found_an_issue = False

    for top_level_agent in G.ESP_JOB.top_level_agents:

        matched_resource_agent = False
        for resource_agent in G.ESP_JOB.resource_agents:

            if resource_agent.upper() == 'THR_AGENT_{0}'.format(top_level_agent.upper()):
                matched_resource_agent = True
                break

        if not matched_resource_agent:

            found_an_issue = True

            this_object_nm = '{0}.{1}'.format(
                G.ESP_JOB.file_basename,
                top_level_agent)

            report_firm_finding(
                object_type_nm='ESP RESOURCE AGENT',
                object_nm=this_object_nm,
                severity=G.RULES[G.RULE_ID].severity,
                message='A top-level agent resource dependency was not recognized for {0}.'.format(
                    top_level_agent),
                class_object=G.ESP_JOB)

        # print (G.ESP_JOB)

        elif G.VERBOSE:
            indent_debug('Notice       : ESP file {0} has set toplevel agent resource_dependency: {1}'.format(
                G.ESP_JOB.file_basename,
                top_level_agent))

    for G.ESP_STEP in G.ESP_JOB.esp_step:
        if G.ESP_STEP.agentname != '':
            matched_resource_agent = False

            if G.ESP_STEP.resource_agent.upper() == 'THR_AGENT_{0}'.format(G.ESP_STEP.agentname.upper()):
                matched_resource_agent = True

            else:
                for resource_agent in G.ESP_JOB.resource_agents:

                    if resource_agent.upper() == 'THR_AGENT_{0}'.format(G.ESP_STEP.agentname.upper()):
                        matched_resource_agent = True
                        break

            if not matched_resource_agent:
                found_an_issue = True

                this_object_nm = '{0}.{1}'.format(
                    G.ESP_JOB.file_basename,
                    G.ESP_STEP.job_name)

                report_firm_finding(
                    object_type_nm='ESP RESOURCE AGENT',
                    object_nm=this_object_nm,
                    severity=G.RULES[G.RULE_ID].severity,
                    message='Agent resource dependency was not set in step {0}.'.format(
                        G.ESP_STEP.job_name),
                    class_object=G.ESP_JOB)

    if not found_an_issue and G.VERBOSE:
        indent_debug('Good         : ESP file {0} no step agent resource dependencies are missing'.format(
            G.ESP_JOB.file_basename))

    return found_an_issue


# ===============================================================================
def check_r716():
    G.RULE_ID = 'r716'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r716_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP files have a missing agent dependency.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP file has a missing agent dependency.')

    elif G.VERBOSE:
        indent('Good         : No ESP files have a missing agent dependency.')
