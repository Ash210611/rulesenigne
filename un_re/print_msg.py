# pylint: disable=C0209			# Don't require formatted strings.
# pylint: disable=W0702			# Allow bare excepts
# pylint: disable=R0914			# Use as many local variables as you need
# pylint: disable=R0912			# llow more branches

import re

import un_re.class_definitions as C
import un_re.global_shared_variables as G

from un_re.fprint import fprint
from un_re.binary_search import binary_search
from un_re.get_comt_user_id import get_comt_user_id
from un_re.indent_info import indent_info
from un_re.notice_file_findings import notice_file_findings


# ======== ========= ========= ========= ========= ========= ========= ==========
def write_junit_dat_file(severity, msg, class_object):
    """
    Save the data now that will be used to write the JUnit.output.xml
    file later.
    """

    href = """https://confluence.sys.cigna.com/pages/viewpage.action?spaceKey=IM&title=Teradata+SQL+coding+Best+Practices"""

    if len(G.JUNIT_DAT_FILENAME) == 0:
        return

    with open(G.JUNIT_DAT_FILENAME, 'a', encoding='utf-8') as junit_file:
        if class_object is None:
            # This can happen when we haven't even opened the
            # filename yet because it has non-utf-8 characters.

            junit_file.write('JUnit|{0}|{1}|{2}|{3}\n'.format(
                severity,
                0,
                'Unknown filename, see console log.',
                msg))
        else:
            junit_file.write('JUnit|{0}|{1}|{2}|{3}\n'.format(
                severity,
                class_object.filenum + 1,  # G.FILE_NUM+1,
                class_object.input_filename_rel,  # G.INPUT_FILENAME_REL,
                msg))

        # Write the SQL statement if possible
        junit_file.write('SQL\n')

        if class_object is None:
            junit_file.write('None.  Review console output instead.\n\n')
        else:
            try:
                junit_file.write('{0}\n\n'.format(class_object.sql_statement))
            except AttributeError:
                junit_file.write('Unknown Statement. Please review the console output instead.\n\n')

        if G.RULES_ENGINE_TYPE == 'TERADATA_DML':
            junit_file.write('More info here: {0}\n'.format(href))
        junit_file.write('END_SQL\n')


# ======== ========= ========= ========= ========= ========= ========= ==========
def write_postgres_json_file(class_object, object_type_nm, object_nm):
    '''
    Whenever a finding is reported (either an error or a warning), log that
    record into a json file to be loaded into the Postgres database at the
    end of the Rules Engine.
    '''

    if hasattr(class_object, 'sql_stmt_num'):
        sql_stmt_num = class_object.sql_stmt_num
    else:
        sql_stmt_num = 0

    ruleset = 'UNKNOWN'  # Default value
    user_story_id = 'UNKNOWN'  # Default value

    for file_obj in G.INPUT_FILES:
        if file_obj.input_filename == class_object.input_filename:
            ruleset = file_obj.ruleset
            user_story_id = file_obj.user_story_id
            break

    project_nm_json = f'"project_nm":"{G.PROJECT_NAME}"'
    git_branch_nm_json = f'"git_branch_nm":"{G.GIT_BRANCH_NAME}"'
    jenkins_build_num_json = f'"jenkins_build_num":"{G.JENKINS_BUILD_NUMBER}"'
    jenkins_build_ts_json = f'"jenkins_build_ts":"{G.JENKINS_BUILD_TS}"'
    input_file_nm_json = '"input_file_nm":"{0}"'.format(
        class_object.input_filename.replace(G.WORKSPACE + '/', ''))

    try:
        comt_user_id = get_comt_user_id(class_object.input_filename)
        comt_user_id = comt_user_id.strip()

        comt_user_id = re.sub(r'internal\\', '', comt_user_id, re.IGNORECASE)
    # For a user id like 'internal\M71647', the \M causes a problem later.
    # We can easily avoid that problem by just removing it.

    except:
        comt_user_id = 'UNKNOWN'

    if comt_user_id != 'UNKNOWN':
        indent_info((' ' * 15) + \
                    'File Chgd by : {0}'.format(comt_user_id))
    comt_user_id_json = '"comt_user_id":"{0}"'.format(comt_user_id)

    indent_info('Filename     : {0}'.format(class_object.input_filename.replace(
        G.INPUT_DIR + '/', '')))

    ruleset_nm_json = '"ruleset_nm":"{0}"'.format(ruleset)
    user_story_id_json = '"user_story_id":"{0}"'.format(user_story_id)
    object_type_nm_json = '"object_type_nm":"{0}"'.format(object_type_nm)

    object_nm_json = object_nm.strip('"')  # To handle quoted column names
    object_nm_json = '"object_nm":"{0}"'.format(object_nm_json)

    rule_id_json = '"rule_id":"{0}"'.format(G.RULE_ID)
    status_cd_json = '"status_cd":"{0}"'.format(G.SEVERITY)

    sql_stmt_num_json = '"sql_stmt_num":"{0}"'.format(sql_stmt_num)

    json_txt = '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}'.format(
        project_nm_json,
        git_branch_nm_json,
        jenkins_build_num_json,
        jenkins_build_ts_json,
        input_file_nm_json,
        comt_user_id_json,
        ruleset_nm_json,
        user_story_id_json,
        object_type_nm_json,
        object_nm_json,
        rule_id_json,
        status_cd_json,
        sql_stmt_num_json)

    json_txt = '{ ' + json_txt + ' }'

    with open(G.POSTGRES_JSON_FILENAME, 'a', encoding='utf-8') as pg_file:
        fprint(pg_file, json_txt)


# ======== ========= ========= ========= ========= ========= ========= ==========
def report_firm_finding(
        object_type_nm,
        object_nm,
        severity,
        message,
        class_object):
    '''
    This function will call print_and_log_msg for rulesets that are not adjustable.
    '''

    G.SEVERITY = severity

    msg_prefix = '{0}-{1}'.format(
        G.SEVERITY,
        G.RULE_ID)

    msg = '{0:12s} : {1}'.format(
        msg_prefix,
        message)

    print_and_log_msg(msg, class_object)

    if class_object is not None:
        # The class object can be None for example when the project
        # like hcta_datalake, is granted for rule g011,
        # and the get_antlr_findings function is still building the
        # class object for the table.

        # Since there is an exception, we can skip post the event for it.

        write_postgres_json_file(
            class_object,
            object_type_nm,
            object_nm)

    if class_object is not None:
        notice_file_findings(class_object.input_filename)


# ======== ========= ========= ========= ========= ========= ========= ==========
def format_msg(severity, message):
    G.SEVERITY = severity
    msg_prefix = '{0}-{1}'.format(G.SEVERITY, G.RULE_ID)
    msg = '{0:12s} : {1}'.format(msg_prefix, message)

    return msg


# ======== ========= ========= ========= ========= ========= ========= ==========
def check_techdebt_limits(class_object, msg, adjusted_message, object_nm, key, ruleset):
    techdebt_termlimit_exceeded = False
    techdebt_excluded = False
    techdebt_usage_count_exceeded = False

    debt = C.UnclearedTechdebt(0, '')  # Initialize for pylint.

    if key in G.RULESET_SEVERITIES:

        if ruleset == 'TECHDEBT':
            input_filename_rel = class_object.get_input_filename_rel()

            for debt in G.UNCLEARED_TECHDEBT:
                if debt.input_file_nm == input_filename_rel:
                    if debt.days_ago > G.MAX_UNCLEARED_TECHDEBT_DAYS:
                        techdebt_termlimit_exceeded = True
                        break

            if not techdebt_termlimit_exceeded:
                # Also check if the TechDebt is excluded.
                techdebt_excluded = binary_search(G.TECHDEBT_EXCLUSIONS, object_nm.split('.')[-1])

            if not techdebt_excluded:
                G.TECHDEBT_USAGE_COUNT += 1

            if G.TECHDEBT_USAGE_COUNT > G.TECHDEBT_USAGE_LIMIT:
                techdebt_usage_count_exceeded = True

        if techdebt_termlimit_exceeded or techdebt_excluded or techdebt_usage_count_exceeded:
            pass
        # Keep the default message already set

        else:
            msg = format_msg(G.RULESET_SEVERITIES[key], adjusted_message)

    print_and_log_msg(msg, class_object)

    if techdebt_termlimit_exceeded:
        indent_info('Notice       : Techdebt usage is disallowed as uncleared for {0} days.'.format(debt.days_ago))
    elif techdebt_excluded:
        indent_info('Notice       : Object {0} is excluded from being managed as Techdebt.'.format(object_nm))
    elif techdebt_usage_count_exceeded:
        indent_info('Notice       : Techdebt used {0} times exceeds the limit of {1}.'.format(
            G.TECHDEBT_USAGE_COUNT,
            G.TECHDEBT_USAGE_LIMIT))


# ======== ========= ========= ========= ========= ========= ========= ==========
def report_adjustable_finding(
        object_type_nm,
        object_nm,
        normal_severity,
        normal_message,
        adjusted_message,
        class_object):
    '''
    This function will call print_and_log_msg adjusted for ruleset severities.

    '''

    # Remove attributes reported in the object_nm, for example by r299
    object_nm = object_nm.split(' ')[0]
    object_nm = object_nm.split('.')[-1]

    # Set the default msg
    msg = format_msg(normal_severity, normal_message)

    ruleset = G.INPUT_FILES[class_object.filenum].ruleset
    key = '{0}|{1}|{2}'.format(
        ruleset,
        G.RULE_ID.upper(),
        normal_severity)

    check_techdebt_limits(class_object, msg, adjusted_message, object_nm, key, ruleset)

    write_postgres_json_file(
        class_object,
        object_type_nm,
        object_nm)

    if class_object is not None:
        notice_file_findings(class_object.input_filename)


# ======== ========= ========= ========= ========= ========= ========= ==========
def print_msg(msg):
    msg_len = len(msg)

    if re.search(r'\bERROR\b', msg):
        G.LOGGER.error('               ' + '*' * msg_len)
        G.LOGGER.error('               ' + msg)
        G.LOGGER.error('               ' + '*' * msg_len)

    elif msg.find('WARNING') > -1:
        G.LOGGER.warning('               ' + '*' * msg_len)
        G.LOGGER.warning('               ' + msg)
        G.LOGGER.warning('               ' + '*' * msg_len)

    else:
        G.LOGGER.info('               ' + '*' * msg_len)
        G.LOGGER.info('               ' + msg)
        G.LOGGER.info('               ' + '*' * msg_len)

    if G.RULE_ID in G.SHOULD_CHECK_RULE:
        if G.RULES[G.RULE_ID].url:
            G.LOGGER.info('               See also     : ' + G.RULES[G.RULE_ID].url)


# ======== ========= ========= ========= ========= ========= ========= ==========
def log_msg(msg, class_object=None):
    if re.search(r'\bERROR\b', msg):

        # G.ERROR_FILENAME = G.TEMP_DIR + "/Rules_Engine.errors"
        # That filename is set by the initialize_env_variables function

        with open(G.ERROR_FILENAME, "a", encoding='utf-8') as out_file:
            if class_object is not None:
                out_file.write('Filenum, name: {0}, {1}\n'.format(
                    class_object.filenum + 1,
                    class_object.input_filename_rel))

            out_file.write(msg + '\n')

        write_junit_dat_file('ERROR', msg, class_object)

    elif msg.find('WARNING') > -1:

        # G.WARNING_FILENAME = G.TEMP_DIR + "/Rules_Engine.warnings"
        # That filename is set by the initialize_env_variables function

        with open(G.WARNING_FILENAME, "a", encoding='utf-8') as out_file:
            if class_object is not None:
                out_file.write('Filenum, name: {0}, {1}\n'.format(
                    class_object.filenum + 1,
                    class_object.input_filename_rel))
                write_junit_dat_file('WARNING', msg, class_object)

            out_file.write(msg + '\n')


# ======== ========= ========= ========= ========= ========= ========= ==========
def print_and_log_msg(msg, class_object=None):
    """
    Print a message line, with a line of asterisks above and below it.
    This is useful for error messages and warnings

    We will also write record labeled for the JUnit output, to be processed
    at the end when the summary is printed.

    The print_msg and log_msg functions are factored separately this way
    for usage where you want to just want to print a message without
    logging it, for example, when the message will be reported again
    later WITH logging.
    """

    if G.TEMP_DIR == '':
        return

    print_msg(msg)

    log_msg(msg, class_object)
