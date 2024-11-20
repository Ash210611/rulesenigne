# pylint: disable=C0209			# Don't require formatted strings

import os
import re

import un_re.global_shared_variables as G

from un_re.fprint import fprint


# ======== ========= ========= ========= ========= ========= ========= ==========
def post_a_success_event_record(file_obj):
    '''
    If a file is finished without any reports of error or warnings from that
    file, then logs that success record into the json file to be loaded into
    the Postgres database at the end of the Rules Engine.
    '''

    if os.path.exists(G.POSTGRES_JSON_FILENAME):
        with open(G.POSTGRES_JSON_FILENAME, 'r', encoding='utf-8') as pg_file:
            # Only post a success record if the input filename is not
            # referenced by any errors or warnings.
            # The file_obj.num_findings == 0 if no errors or warnings
            # were found from any rules, which are checked in series.
            # But syntax errors are reported by Antlr during the parallel
            # stage, which only persists that finding in the Warning file,
            # not in the class object

            for line in pg_file.readlines():
                if re.search(file_obj.input_filename_rel, line):
                    return

    project_nm = f'"project_nm":"{G.PROJECT_NAME}"'
    git_branch_nm = f'"git_branch_nm":"{G.GIT_BRANCH_NAME}"'
    jenkins_build_num = f'"jenkins_build_num":"{G.JENKINS_BUILD_NUMBER}"'
    jenkins_build_ts = f'"jenkins_build_ts":"{G.JENKINS_BUILD_TS}"'
    input_file_nm = '"input_file_nm":"{0}"'.format(
        file_obj.input_filename.replace(G.WORKSPACE + '/', ''))
    comt_user_id = '"comt_user_id":"N/A"'
    ruleset_nm = '"ruleset_nm":"{0}"'.format(file_obj.ruleset)
    user_story_id = '"user_story_id":"{0}"'.format(file_obj.user_story_id)
    object_type_nm = '"object_type_nm":"ALL"'
    object_nm = '"object_nm":"ALL"'
    rule_id = '"rule_id":"ALL"'
    status_cd = '"status_cd":"SUCCESS"'

    json_txt = '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}'.format(
        project_nm,
        git_branch_nm,
        jenkins_build_num,
        jenkins_build_ts,
        input_file_nm,
        comt_user_id,
        ruleset_nm,
        user_story_id,
        object_type_nm,
        object_nm,
        rule_id,
        status_cd)

    json_txt = '{ ' + json_txt + ' }'

    with open(G.POSTGRES_JSON_FILENAME, 'a', encoding='utf-8') as pg_file:
        fprint(pg_file, json_txt)


# ===============================================================================
def post_success_event_records():
    for file_obj in G.INPUT_FILES:
        if file_obj.num_findings == 0:
            post_a_success_event_record(file_obj)

    # Return the total number of records in the JSON file.
    total_num_json_records = 0
    if os.path.exists(G.POSTGRES_JSON_FILENAME):
        # Just being paranoid about that.

        with open(G.POSTGRES_JSON_FILENAME, 'r', encoding='utf-8') as pg_file:
            for _ in pg_file.readlines():
                total_num_json_records += 1

    return total_num_json_records
