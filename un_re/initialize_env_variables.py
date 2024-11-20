# pylint: disable=C0209				# Don't require formatted strings
# pylint: disable=W1203				# Don't require lazy logger formatting

from datetime import datetime
import importlib
import os
import re
import sys

import un_re.global_shared_variables as G
import un_re.ERROR_NUMBERS as E

from un_re.antlr_parse_stmt import antlr_parse_stmt
from un_re.get_1_env_value import get_1_env_value
from un_re.indent import indent
from un_re.setup_logging import set_verbose_logging

from un_re.populate_workspace_tokens import populate_workspace_tokens


# ======== ========= ========= ========= ========= ========= ========= ==========
def display_env_variables():
    indent('')
    indent('The available env variables are:')
    sorted_environ = sorted(os.environ.items())
    for name, value in sorted_environ:
        indent("{0}: {1}".format(name, value))

    indent('')


# ======== ========= ========= ========= ========= ========= ========= ==========
def set_git_branch_name():
    '''
    For Hadoop-D, typical available environmental variables are
        gitlabBranch=develop

    This variable does not appear to have an appropriate value:
        GIT_BRANCH=origin/staticedgenode_migration
    '''

    G.GIT_BRANCH_NAME = os.environ.get('BRANCH', 'UNKNOWN')

    if G.GIT_BRANCH_NAME == 'UNKNOWN':
        G.GIT_BRANCH_NAME = os.environ.get('feature_branch', 'UNKNOWN')

    if G.GIT_BRANCH_NAME == 'UNKNOWN':
        G.GIT_BRANCH_NAME = os.environ.get('gitlabBranch', 'UNKNOWN')

    if G.GIT_BRANCH_NAME == 'UNKNOWN':
        G.LOGGER.info('WARNING : Cannot find the Git BRANCH environmental variable.')
        display_env_variables()

    G.LOGGER.info(f'BRANCH NAME  = {G.GIT_BRANCH_NAME}')


# ======== ========= ========= ========= ========= ========= ========= ==========
def set_jenkins_build_number():
    G.JENKINS_BUILD_NUMBER = os.environ.get('BUILD_NUMBER', '-1')
    if G.JENKINS_BUILD_NUMBER == '-1':
        G.LOGGER.info('WARNING : Cannot find the Jenkins BUILD_NUMBER environmental variable.')
    G.LOGGER.info(f'JENKINS BUILD= {G.JENKINS_BUILD_NUMBER}')


# ======== ========= ========= ========= ========= ========= ========= ==========
def set_project_name_from_cloudbees():
    '''
    The enviroment variable JOB is read and saved as the global
    G.JENKINS_JOB_NAME.

    For example, if:
        if G.JENKINS_JOB_NAME = 'orchestrators-folders/sql-rules-engine/UN_RE/UN_RE_DAMODRE'
    then
        G.PROJECT_NAME = 'UN_RE_DAMODRE'
    '''

    G.PROJECT_NAME = G.JENKINS_JOB_NAME.split('/')[-2]

    if G.PROJECT_NAME == 'UN_RE':
        G.PROJECT_NAME = G.JENKINS_JOB_NAME.split('/')[-1]


# ======== ========= ========= ========= ========= ========= ========= ==========
def set_project_name_from_imjenkins():
    G.JENKINS_JOB_NAME = G.JENKINS_JOB_NAME.replace('develop1-pipeline', 'develop1_pipeline')

    try:
        # Suppose JOB_NAME	= 'CCW-D/eval-develop1_pipeline'
        # Or suppose JOB_NAME	= 'hadoop-d/hedis/develop-pipeline'
        # Or suppose JOB_NAME	= 'CCW-D/testing-Testing_pipeline'

        rev_job_name = G.JENKINS_JOB_NAME[::-1]
        # print (f'rev_job_name = {rev_job_name}')
        # rev_job_name 		= 'enilepip_1poleved-lave/D-WCC'
        # rev_job_name		= 'enilepip-poleved/sideh/d-poodah'
        # rev_job_name		= 'enilepip_gnitseT-gnitset/D-WCC'

        rev_part_1 = rev_job_name.split('-', 1)[1]
        # print (f'rev_part_1   = {rev_part_1}')
        # rev_part_1 		= 'lave/D-WCC'
        # rev_part_1		= 'poleved/sideh/d-poodah'
        # rev_part_1		= 'gnitset/D-WCC'

        G.PROJECT_NAME = rev_part_1[::-1]
        # print (f'G.PROJECT_NAME = {G.PROJECT_NAME}')
        # G.PROJECT_NAME 	= 'CCW-D/eval'
        # G.PROJECT_NAME	= 'hadoop-d/hedis/develop'
        # G.PROJECT_NAME	= 'CCW-D/testing'

        # Remove the GIT_BRANCH if it is still there.
        # Like it was still there in that example for hadoop-d
        G.PROJECT_NAME = re.sub(G.GIT_BRANCH_NAME, '', G.PROJECT_NAME)
        # print (f'G.PROJECT_NAME = {G.PROJECT_NAME}')
        G.PROJECT_NAME = G.PROJECT_NAME.rstrip('/')
    # print (f'G.PROJECT_NAME = {G.PROJECT_NAME}')

    except IndexError:
        G.LOGGER.info('Failed to decode the Jenkins JOB_NAME variable')
        G.LOGGER.info(f'Tried to decode: {G.JENKINS_JOB_NAME}')
        G.JENKINS_JOB_NAME = 'UNKNOWN'
        G.PROJECT_NAME = 'UNKNOWN'

    name_parts = G.PROJECT_NAME.split('/')
    if len(name_parts) > 2:
        G.PROJECT_NAME = '/'.join(name_parts[0:2])


# ======== ========= ========= ========= ========= ========= ========= ==========
def set_project_name():
    '''
    Examples of typical, valid output project names are
        CCW-D/ccb
        CCW-D/clinical
        hadoop-D/blueprint
        hadoop-D/sda

    This function will prune anything after the 2nd '/'
    '''

    G.PROJECT_NAME = os.environ.get('PROJECT_NAME', 'UNKNOWN-PROJECT_NAME')
    G.JENKINS_JOB_NAME = os.environ.get('JOB_NAME', 'UNKNOWN-JOB_NAME')

    if G.PROJECT_NAME == 'UNKNOWN-PROJECT_NAME':
        G.PROJECT_NAME = 'UNKNOWN'

        if G.JENKINS_JOB_NAME == 'UNKNOWN-JOB_NAME':

            G.LOGGER.info('WARNING : Cannot find the Jenkins JOB_NAME environmental variable.')

        else:
            if re.search('orchestrators', G.JENKINS_JOB_NAME, re.IGNORECASE):
                set_project_name_from_cloudbees()
            else:
                set_project_name_from_imjenkins()

    G.LOGGER.info(f'PROJECT NAME = {G.PROJECT_NAME}')


# ======== ========= ========= ========= ========= ========= ========= ==========
def get_verbosity():
    if not G.VERBOSE:
        # VERBOSE could be set on the command line with the -v option,
        # or it could be set in the INI file by saying VERBOSE = 1
        G.VERBOSE = get_1_env_value(G.INI_FILENAME, "VERBOSE", True)

        if G.VERBOSE in ("1", 'TRUE'):
            G.VERBOSE = True
            G.LOGGER.info('VERBOSE      = True')
            set_verbose_logging()
        else:
            G.VERBOSE = False
    else:
        G.LOGGER.info('VERBOSE      = True')
        set_verbose_logging()


# ======== ========= ========= ========= ========= ========= ========= ==========
def set_load_event_records():
    if G.GET_CFG_FROM_GIT:
        G.LOAD_EVENT_RECORDS = False
        # If you can't read from the DMV,
        # you can't write to it either.
        return

    temp_flag = get_1_env_value(G.INI_FILENAME, "LOAD_EVENT_RECORDS", is_optional=True)
    if temp_flag:
        if temp_flag == 'FALSE':
            G.LOAD_EVENT_RECORDS = False
        else:
            G.LOAD_EVENT_RECORDS = True


# else it defaults to True

# ======== ========= ========= ========= ========= ========= ========= ==========
def read_list_of_rules_to_skip():
    '''
    This would be comma-delimited list of rules to skip, read from the
    pipeline, rather than from the exception table.

    '''
    temp_rules_to_skip = get_1_env_value(G.INI_FILENAME, "RULES_TO_SKIP", is_optional=True)
    if temp_rules_to_skip:
        G.RULES_TO_SKIP = []
        for temp_rule in temp_rules_to_skip.split(','):
            temp_rule = temp_rule.strip()
            G.RULES_TO_SKIP.append(temp_rule)


# ======== ========= ========= ========= ========= ========= ========= ==========
def set_dir_scan_type():
    G.DIR_SCAN_TYPE = get_1_env_value(G.INI_FILENAME, "DIR_SCAN_TYPE", is_optional=True)
    if G.DIR_SCAN_TYPE is None:
        G.DIR_SCAN_TYPE = 'FULL'
    elif G.DIR_SCAN_TYPE == 'FULL':
        pass
    elif G.DIR_SCAN_TYPE == 'RECENT':
        pass
    else:
        G.LOGGER.error(f'ERROR: Unknown value for DIR_SCAN_TYPE: {G.DIR_SCAN_TYPE}')
        sys.exit(E.UNKNOWN_DIR_SCAN_TYPE)


# ======== ========= ========= ========= ========= ========= ========= ==========
def set_ORE_variables():
    if G.RULES_ENGINE_TYPE == 'ORE':
        G.XML_FILENAME = get_1_env_value(G.INI_FILENAME, "XML_FILENAME", is_optional=True)
        # if G.XML_FILENAME is None:
        # 	G.XML_FILENAME = G.WORKSPACE + '/master.xml'
        # 	# else it was specified in the INI file by the parent process.
        # No, if they want to use an XML_FILE, they need to specify using it.

        temp_antlr_timeout = get_1_env_value(G.INI_FILENAME, "ANTLR_TIMEOUT_SECONDS", is_optional=True)
        if temp_antlr_timeout is not None:
            G.ANTLR_TIMEOUT_SECONDS = int(temp_antlr_timeout)
            # Reload any modules that need to recognize the new timeout value
            if 'un_re.antlr_parse_stmt' in sys.modules:
                importlib.reload(sys.modules.get(antlr_parse_stmt.__module__))
            G.LOGGER.info(f'ANTLR TIMEOUT= {G.ANTLR_TIMEOUT_SECONDS} seconds.')

        temp_cmd_limit = get_1_env_value(G.INI_FILENAME, "MAX_CMDS_PER_TYPE_PER_FILE", is_optional=True)
        if temp_cmd_limit is not None:
            G.MAX_CMDS_PER_TYPE_PER_FILE = temp_cmd_limit
        G.LOGGER.info(f'Command Limit= {G.MAX_CMDS_PER_TYPE_PER_FILE} commands, per type, per file')


# ======== ========= ========= ========= ========= ========= ========= ==========
def set_get_cfg_from_git():
    G.GET_CFG_FROM_GIT = get_1_env_value(G.INI_FILENAME, "GET_CFG_FROM_GIT", is_optional=True)
    if G.GET_CFG_FROM_GIT is None:
        G.GET_CFG_FROM_GIT = False
    elif G.GET_CFG_FROM_GIT == 'True':
        G.GET_CFG_FROM_GIT = True
    else:
        G.GET_CFG_FROM_GIT = False

    if G.GET_CFG_FROM_GIT:
        G.LOAD_EVENT_RECORDS = False
    # If you can't read from the DMV,
    # you can't write to it either.


# ======== ========= ========= ========= ========= ========= ========= ==========
def get_certificate_location():
    """
    The default certificate location is G.CERTIFICATE_LOCATION.
    """

    temp_cl = os.environ.get('CERTIFICATE_LOCATION', 'UNKNOWN')
    if temp_cl != 'UNKNOWN':
        G.CERTIFICATE_LOCATION = temp_cl

    if not os.path.exists(G.CERTIFICATE_LOCATION):
        G.LOGGER.error('Error: The certificate location is not found.')
        G.LOGGER.error('Error: This is doomed to fail.')
        G.LOGGER.error(f'Error: Tried to find: {G.CERTIFICATE_LOCATION}')


# ======== ========= ========= ========= ========= ========= ========= ==========
def initialize_env_variables():
    """
    This application uses a lot of input variables.

    The user-specified input variables are entered on the screen from a
    Jenkins job.   There are too many variables to put on a reasonable command
    line, so Jenkins saves them in a file, and puts the name of that 1 file
    on the command line.

    Additional variables are saved in support files.
    For example, the KNOWN_DB.dat file specifies the list of known databases.
    """

    # Set the error filename first, in case you need to report an error
    # while getting one of the env variables, hopefully not!
    G.ERROR_FILENAME = G.TEMP_DIR + "/Rules_Engine.errors"
    G.WARNING_FILENAME = G.TEMP_DIR + "/Rules_Engine.warnings"
    G.JUNIT_DAT_FILENAME = G.WORKSPACE + "/JUnit.Rules_Engine.output.dat"
    G.JUNIT_XML_FILENAME = G.WORKSPACE + "/JUnit.Rules_Engine.output.xml"

    # Read the variables in the INI file
    G.RULES_ENGINE_TYPE = get_1_env_value(G.INI_FILENAME, "RULES_ENGINE_TYPE", False)

    G.INPUT_DIR = get_1_env_value(G.INI_FILENAME, "INPUT_DIR", is_optional=True)
    if G.INPUT_DIR is None:
        G.INPUT_DIR = get_1_env_value(G.INI_FILENAME, "INPUT_SQL_DIR", is_optional=True)
    # If the INPUT_DIR is still None, it won't pass the validate_input_args function

    G.ALTERNATIVE_RULES_LIST = get_1_env_value(G.INI_FILENAME, "ALTERNATIVE_RULES_LIST", is_optional=True)

    set_ORE_variables()

    if G.RULES_ENGINE_TYPE in ('TERADATA_DDL', 'PG_RE', 'DB2_RE',
                               'DATABRICKS', 'SNOWFLAKE', 'REDSHIFT', 'HIVE_DDL_RE'):
        G.XML_FILENAME = get_1_env_value(G.INI_FILENAME, "XML_FILENAME", is_optional=True)

    if G.RULES_ENGINE_TYPE == 'TERADATA_DDL':
        if G.XML_FILENAME is None:
            G.XML_FILENAME = G.WORKSPACE + '/teradata/liquibase.xml'
    # else it was specified in the INI file by the parent process.
    # Don't initialize the XML_FILENAME for any other rules engine types.
    # The other rules engine types either need to specify the INPUT_DIR to do a directory scan.
    # or an XML_FILENAME to list a specific list of files to scan.

    G.Z_FILE = G.SCRIPT_DIR + '/un_re/resources/Rules_Engine.expected.z'

    get_verbosity()

    temp_num = get_1_env_value(G.INI_FILENAME, "NUM_DAYS_TO_SAVE_LOG_FILES", is_optional=True)
    if temp_num:
        G.NUM_DAYS_TO_SAVE_LOG_FILES = int(temp_num)
    else:
        G.NUM_DAYS_TO_SAVE_LOG_FILES = 1

    temp_num = get_1_env_value(G.INI_FILENAME, "PARALLEL_DEGREE", is_optional=True)
    if temp_num:
        G.PARALLEL_DEGREE = int(temp_num)
    else:
        G.PARALLEL_DEGREE = 1

    set_dir_scan_type()

    set_load_event_records()

    populate_workspace_tokens()

    read_list_of_rules_to_skip()

    # =======================================================================
    # Get variables used for the ESP_RE
    if G.RULES_ENGINE_TYPE == 'ESP_RE':
        G.ESP_ENVIRONMENT = get_1_env_value(G.INI_FILENAME, "ESP_ENVIRONMENT", False)
        G.ESP_JOB_NAME_LENGTH_LIMIT = get_1_env_value(G.INI_FILENAME, "ESP_JOB_NAME_LENGTH_LIMIT", False)

        G.ESP_JOB_NAME_LENGTH_LIMIT = int(G.ESP_JOB_NAME_LENGTH_LIMIT)

    # =======================================================================
    # Get variables from the Linux environment

    set_git_branch_name()
    set_jenkins_build_number()
    set_project_name()

    G.POSTGRES_JSON_FILENAME = G.WORKSPACE + \
                               "/rules_engine_findings.{0}.json".format(
                                   G.START_TIME)

    G.JENKINS_BUILD_TS = datetime.now()

    set_get_cfg_from_git()

    get_certificate_location()
