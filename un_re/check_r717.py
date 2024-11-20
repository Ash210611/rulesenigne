# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r717_for_1_esp_job():
    found_an_issue = False

    if G.ESP_JOB.BUC_code != '':

        if G.ESP_JOB.resource_buc_code == '':
            found_an_issue = True

            report_firm_finding(
                object_type_nm='ESP RESOURCE BUC CODE',
                object_nm=G.ESP_JOB.file_basename,
                severity=G.RULES[G.RULE_ID].severity,
                message='Top-level buc_code resource dependency was not set.',
                class_object=G.ESP_JOB)

        elif not re.search(r'THR_{0}_MAINT'.format(G.ESP_JOB.BUC_code), G.ESP_JOB.resource_buc_code):
            found_an_issue = True

            report_firm_finding(
                object_type_nm='ESP RESOURCE BUC CODE',
                object_nm=G.ESP_JOB.file_basename,
                severity=G.RULES[G.RULE_ID].severity,
                message='Top-level buc_code resource dependency {0} not recognized.'.format(
                    G.ESP_JOB.resource_buc_code),
                class_object=G.ESP_JOB)

        elif G.VERBOSE:
            indent_debug('Good         : ESP file {0} has set toplevel buc_code resource_dependency: {1}'.format(
                G.ESP_JOB.file_basename,
                G.ESP_JOB.BUC_code))

    return found_an_issue


# ===============================================================================
def check_r717():
    G.RULE_ID = 'r717'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r717_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP files have a missing buc code dependency.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP file has a missing buc code dependency.')

    elif G.VERBOSE:
        indent('Good         : No ESP files have a missing buc code dependency.')
