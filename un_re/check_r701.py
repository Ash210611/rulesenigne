# pylint: disable=C0209           # Don't require formtted strings

import re

import un_re.global_shared_variables as G
from un_re.indent import indent
from un_re.indent_debug import indent_debug
from un_re.indent_info import indent_info
from un_re.print_msg import report_firm_finding


# ===============================================================================
def check_r701_for_1_esp_job():
    '''
    Each ESP job should invoke an appropriate library.

    And it should invoke this library in Prod:
        TTAP.U44.PROD.APPLLIB

    In all other environments, the ESP job should invoke this library:
        TTAT.U44.TEST.APPLLIB
    '''

    found_an_issue = False

    if G.ESP_JOB.invoked_library == '':

        found_an_issue = True
        report_firm_finding(
            object_type_nm='ESP INVOKE',
            object_nm=G.ESP_JOB.file_basename,
            severity=G.RULES[G.RULE_ID].severity,
            message='ESP file did not invoke a library.',
            class_object=G.ESP_JOB)

        indent_info('Notice       : ESP file {0} did not invoke a libary.'.format(
            G.ESP_JOB.file_basename))

    elif (G.ESP_ENVIRONMENT == 'PROD' and
          not re.search(r'TTAP\.U44\.PROD\.APPLLIB', G.ESP_JOB.invoked_library)) or \
            (G.ESP_ENVIRONMENT != 'PROD' and
             not re.search(r'TTAT\.U44\.TEST\.APPLLIB', G.ESP_JOB.invoked_library)):

        found_an_issue = True
        report_firm_finding(
            object_type_nm='ESP INVOKE',
            object_nm=G.ESP_JOB.file_basename,
            severity=G.RULES[G.RULE_ID].severity,
            message='ESP file invoked an invalid library.',
            class_object=G.ESP_JOB)

        indent_info('Notice       : Invoked Library: {0}.'.format(
            G.ESP_JOB.invoked_library))
        indent_info('Notice       : Does not correspond to the {0} environment'.format(
            G.ESP_ENVIRONMENT))

    elif G.VERBOSE:
        indent_debug('Good         : ESP file {0} invoked {1}.'.format(
            G.ESP_JOB.file_basename,
            G.ESP_JOB.invoked_library))

    return found_an_issue


# ===============================================================================
def check_r701():
    G.RULE_ID = 'r701'

    # -----------------------------------------------------------------------
    if not G.RULE_ID in G.SHOULD_CHECK_RULE:
        return

    # -----------------------------------------------------------------------
    G.LOGGER.info('Checking rule {0}...'.format(G.RULE_ID))

    num_esp_jobs_w_findings = 0

    for G.ESP_JOB in G.ESP_JOBS:

        if check_r701_for_1_esp_job():
            num_esp_jobs_w_findings += 1

    if num_esp_jobs_w_findings > 1:
        indent_info('Notice       : {0} ESP files did not invoke the right library.'.format(
            num_esp_jobs_w_findings))

    elif num_esp_jobs_w_findings == 1:
        indent_info('Notice       : 1 ESP file did not invoke the right library.')

    elif G.VERBOSE:
        indent('Good         : All ESP files invoked the right library.')
