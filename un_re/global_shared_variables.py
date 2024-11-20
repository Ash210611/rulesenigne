# This module initializes the internal, global, shared variables that are
# used by many different functions in the rules-engine executable.
#
# While global variables should not be misused, it is convenient to use these,
# rather than simply copy a long list of parameters from one function to the
# next.
#
# Note about the file naming strategy.
# 1) UN_RE will search for files found under the INPUT_DIR. 
#	The current 1 file being processed from INPUT_DIR 
# 	is named INPUT_FILENAME
#
# 2) UN_RE makes a temporary directory called TEMP_DIR.  Each 
#	INPUT_FILENAME is copied from INPUT_DIR to TEMP_DIR, and named
#	LOCAL_SCRIPT_NAME.  That protects the original file from changes
#	until all the tests and rules are checked.
#
# 3) UN_RE makes a subdirectory called TEMP_DIR/tempddl. Each 
#	LOCAL_SCRIPT_NAME is read and used to write the Liquibase-formatted 
#	file called LQB_FILE in the tempddl directory.
#
# ==============================================================================

from typing import Any, Dict, List

import un_re.class_definitions as C
import un_re.class_definitions_base as D  # D for Design

# ==============================================================================
ABBREVIATED_MULTI_TOKENS: List[C.AbbreviatedMultiToken] = []
ABBREVIATED_SINGLE_TOKENS: List[C.AbbreviatedSingleToken] = []
# These are related to the ENTERPRISE_NAMING_STANDARD

ALLOW_RULE_EXCEPTIONS = True

ALTERNATIVE_RULES_LIST = None
# The default list of rules is in a file named:
# resources/rules.{G.RULES_ENGINE_TYPE}.lst
# If this variable is set in the INI file, UN_RE will use that instead.

ANTLR_JAR_FILENAME = 'antlr4-4.13.0-complete.jar'
ANTLR_JAR_SOURCE = \
    'https://repo.sys.cigna.com/artifactory/maven-release-repos/org/antlr/antlr4/4.13.0/'

ANTLR_LOG_FILENAME = ''
ANTLR_LOG_CONTENTS = ''

ANTLR_TIMEOUT_SECONDS = 60

ARRAY_EXCEPTION_LIST: List[C.ArrayException] = []

ARTICLE_LIST: List[C.Article] = []

ATTRIB: D.Attrib
ATTRIBS: List[D.Attrib] = []

AVAILABLE_RULES_TO_CHECK: Dict[str, bool] = {}
# The list of rules that are available to check.  Just because a rule
# is available to be checked does not mean it should be checked.
# The list of available rules is taken from the rules.lst file.  The
# list of rules that should be check are taken from the rules.xxx.lst files.

BAD_CHAR_LIST = []

BUSINESS_TERM_LIST: List[C.BusinessTerm] = []

CCW_BASE_TABLENAME_LIST: List[str] = []
CCW_BASE_COLUMNNAME_LIST: List[str] = []

CERTIFICATE_LOCATION = '/etc/pki/tls/certs/ca-bundle.crt'
# Location of the TLS certificates

CLASSWORD_LIST: List[C.Classword] = []

CLASSWORD_DATATYPES: Dict[str, C.ClasswordDatatype] = {}

CLASSWORD_DATATYPE_VARIATIONS = []
# Most CDs should be Varchar(10)
# Some column names are allowed to have an exception.
# Other classwords can be listed in that structure too.

CLASSWORD_EXCEPTIONS: List[C.ClasswordException] = []

COLUMN_COMMENTS: List[C.ColumnComment] = []

LOGICAL_CLASSWORD_LIST: List[str] = []
# LOGICAL_CLASSWORD_EXCEPTION_LIST: List[str] 	= []
# There are not any of those actually used yet.

PHYSICAL_CLASSWORD_LIST: List[str] = []
PHYSICAL_CLASSWORD_EXCEPTION_LIST: List[str] = []

COLUMN_NAME: str = ''
COLUMN_NAME_PART_LIST = []
# The column name part list

COLUMN_TITLE = ''

COLUMN_ELEMENT: C.Column
COLUMN_ELEMENTS: List[C.Column] = []

COMMAND_REGEXES = {}

COMMAND_TYPE = ''
# Will be CREATE TABLE, CREATE VIEW, etc.

COMMAND_COUNTER: Dict[str, int] = {}
# Keep count of each kind of command.
# That is a useful cross reference that everything is parsed right.

COMMENT_STR = None
# Either a Table or Column comment

COMT_USER_ID: str = 'UNKNOWN'
# That would be the Git Committer ID

# noinspection PyTypeChecker
DATABASE_BASE_DEFAULT: str = None
DATABASE_BASE: str = ''
DATABASE_NUM: int = -1
# Array index in list of KNOWN_DBs

DATATYPE: str = ''

DBX_OPTIMIZE_STMTS = []
# Databricks optimize SQL statements

DECOMMENT_XML: bool = True
# By default, ignore files listed in the liquibase.xml file that are commented out.
# The all domains build wants to read the files included in comments.
# To read all the files, including the files included in comments, set this variable
# to False, by passing -d as a command-line parameter.

# DEV_LOGMECH				= 'TD2'
# DEV_SERVER				= 'LSHTD2.sys.cigna.com'
# DEV_USERNAME				= 'IMAPPDBA'
# DEV_PASSWORD				= None		# Will be read from the environment
# Are these still needed??

DIR_SCAN_TYPE: str = ''
# Will be set to either FULL or RECENT

DISTKEY_COLUMN = None

DKC_ENV = 'dev'
DKC_USERNAME = 'SVT_UNRE_DKC_LOADER'
DKC_PASSWORD = None  # Will be read from the environment

DMV_SERVER = 'cvwappxp20054.internal.cigna.com'
DMV_DATABASE = 'postgres'
DMV_USERNAME = 'rulesengine_adm'
DMV_PASSWORD = None  # Will be read from the environment

ENTERPRISE_NAMING_STANDARD: List[C.Abbreviation] = []
# Holds the list of approved abbreviations.

ENTITY: D.Entity
ENTITIES: List[D.Entity] = []

ERROR_FILENAME: str = ''
# This file summarizes all errors reported by the print_msg function

ESP_ENVIRONMENT = ''
ESP_JOB_NAME_LENGTH_LIMIT = 0

ESP_STEP: C.ESPStep

ESP_JOB: C.ESPJob
# Refers (points) to an ESP_JOB class object
ESP_JOBS: List[C.ESPJob] = []
# The list of ESP_JOB class objects

EXC_FILENAME_LIST: List[str] = []
# Filename in that list will be skipped by the TERADATA_DML rules engine type

EXPECTED_CONTENT: List[str] = []
# Used by rule r401

EXTRNL_NM_LIST = None
# The list of external names will be read from the dmv.extrnl_nm
# and appended to the ENTERPRISE_NAMING_STANDARD.
# They are read separately, but they work like regular abbreviations.

FILE_CONTENTS: str = ''
# Contents of the LOCAL_SCRIPT_NAME

FILE_NUM: int = 0
FILE_OBJ = None
FILE_DICT: Dict[int, str] = {}
# The File dictionary holds the list of files.

GET_CFG_FROM_GIT = False
# If True, will retreive the CFG tables from the Git repo
# not from the DMV and not from the local package
# If True, also will set LOAD_EVENT_RECORDS = False

GIT_BRANCH_NAME: str = ''
# That is the Git Branch name used by the -D pipeline

GIT_URL = 'https://raw.github.sys.cigna.com/cigna/da_unified_rules_engine/master'

GRANT_STATEMENTS = []

HIVE_TABLE_STRUCTURE: C.HiveTableStructure = None
HIVE_TABLE_STRUCTURES: List[C.HiveTableStructure] = []

INDEX_OBJ = None
INDEX_OBJS: List[C.Index_Obj] = []

INI_FILENAME: str = ''
# This file holds the environmental settings for this single run

INPUT_FILENAME: str = ''
INPUT_FILENAME_REL: str = ''

INPUT_FILE = None  # The structure
INPUT_FILES: List[C.InputFile] = []  # The list of structures
# List of Input_File class objects


INPUT_DIR: str = ''
# This is the directory where input files are found.
# Input files might be SQL, or ESP jobs, or Erwin extracts.

JENKINS_BUILD_NUMBER: str = ''
# That is the Jenkins build number of the -D pipeline

JENKINS_BUILD_TS: str = ''
# Timestamp when the Jenkins build ran.

JENKINS_JOB_NAME: str = ''

JOB_NAME: str = ''
# That is the Jenkins Job Name of the -D pipeline

JSON_RECORD: Dict[str, Any] = {}
# These JSON records are used by the DATA_MODEL rules engine
# holding input from the Erwin API Extract
JSON_RECORDS: Dict[str, Any] = {}

JUNIT_DAT_FILENAME: str = ''
# Holds the data destined for the JUNIT_XML_FILENAME
# The JUNIT_DAT_FILENAME is only written by TERADATA_DML, not by TERADATA_DDL

JUNIT_XML_FILENAME: str = ''
# The full path to the JUnit.output.xml file

LIST_OF_SPLIT_FILENAMES: List[str] = []

LOAD_EVENT_RECORDS: bool = True

LOCAL_SCRIPT_NAME: str = ''

LOG_FILENAME: str = ''
# That is the main log file.   If parallelism is used, then
# the contents of THREAD_LOG_FILENAME will be appended as they finish

LOGGER: Any = None

MAX_CMDS_PER_TYPE_PER_FILE = 20
# If they put more commands per type than that, like INSERTs,
# in one file, they should move those to ETL

MAX_UNCLEARED_TECHDEBT_DAYS = 125

MODEL: D.Model
MODELS: List[D.Model] = []
# Erwin API Extract models

MULTISET_BASE_TABLES: List[C.MultisetBaseTable] = []
# That list is used by R415

NAME_LENGTH_LIMIT: int = 128
# Table and Column names should not exceed that.

NUM_DAYS_TO_SAVE_LOG_FILES = 2

OBJECT_NM = ''
# The specific name of the object for reporting findings.

OBJECT_TYPE_NM = ''
# Used when reporting findings
# Will be things like Table name, Column name, comment, etc

OTHER_STATEMENT: C.OtherStatement
OTHER_STATEMENTS: List[C.OtherStatement] = []
# Other statements are stored in the OTHER_Statement class object

PARALLEL_DEGREE = 1

PG_CONNECTION = None
# Save the connection handle in a global to be reused again.

POSTGRES_JSON_FILENAME = ''
# Holds the reported findings in a json format
# to be inserted into the Postgres historical repository.

PROJECT_NAME = ''
# Used for reporting JSON events

# noinspection PyTypeChecker
REDSHIFT_TABLE_STRUCTURE: C.RedshiftTableStructure = None
REDSHIFT_TABLE_STRUCTURES: List[C.RedshiftTableStructure] = []

RULES_ENGINE_TYPE: str = ''
# The valid values are:
# 	TERADATA_DDL
# 	TERADATA_DML
# 	DAMODRE
#	HIVE_DDL_RE
#	PG_RE

RULE_ID = ''

RULES: Dict[str, C.Rule] = {}

RULES_EXCEPTION: List[C.RulesException] = []
# See comments in the resources/rules_exceptions.lst file

RULES_TO_SKIP = []
# This list of rules to skip is read from the INI file.
# They SHOULD be managed using the RULES_EXCEPTION list.
# This list enables the pipeline developer to select
# which rules to exclude when developing a pipeline.

RULESET_SEVERITIES: Dict[str, str] = {}

SCRIPT_DIR = ''
# The launch directory for this script

SCRIPT_NAME = ''
# The name of this script

SEVERITY = ''
# Will be set to ERROR, WARNING, Notice, or Good

SHA_LIST: List[str] = []
# List of GitLab commit SHA's

SHOULD_CHECK_RULE: Dict[str, bool] = {}
# Cross reference this list with the AVAILABLE_RULE_TO_CHECK list.
# A rule should only be checked if it is also listed there.

SQL_STATEMENT: str = ''
# The current sql statement being checked.
# This is provided for convenience

SQL_STATEMENT_OBJ: C.SQLStatementObj
SQL_STATEMENT_OBJS: List[C.SQLStatementObj] = []
# An instance and array of the SQL_Statement_Obj class object

SQL_STMT_NUM = -1
# Index to the current sql_statement

START_TIME = ''
# String date, format YYYY-MM-DD_H.M.S. Avoid colons, which would
#       make it not suitable for usage in filenames.

SUBJCT_AREA: D.Subjct_Area
SUBJCT_AREAS: List[D.Subjct_Area] = []
# Erwin API subject area from models

SYSTEM_OS = ''

TABLE_COMMENT = None
TABLE_COMMENTS = []

TABLE_NAME: str = ''
# Replace that with G.TABLE_STRUCTURE.table_name_orig
# Could be a Table Name or a View name

TABLE_NAME_PART_LIST: List[str] = []
# Holds the tokens from the TABLE_NAME

# noinspection PyTypeChecker
TABLE_STRUCTURE: C.TableStructure = None
TABLE_STRUCTURES: List[C.TableStructure] = []

TECHDEBT_EXCLUSIONS: List[str] = []

TECHDEBT_EXCLUSION_OBJS: List[C.TechdebtExclusion] = []

TECHDEBT_USAGE_COUNT = 0
TECHDEBT_USAGE_LIMIT = 50

TEMP_DIR = ''
# All temporary files will be written to there

TENTATIVE_COMMAND_TYPE = ''

THREAD_LOG_FILENAME = ''
# That is the log file for a single thread when parallelism is used.

UNCLEARED_TECHDEBT = []
# List of DDL files that have uncleared Techdebt

USERID = ''

VALID_BUC_CODE_LIST: List[str] = []

VERBOSE = False
# If True, will generate additional output for testing purposes

VERSIONS_FILENAME = None
# Holds the list of Git Commit SHAs
# Only used in a Pytest.

VIEW_NAME = ''
VIEW_STRUCTURE = None
VIEW_STRUCTURES: List[C.ViewStructure] = []

WARNING_FILENAME = ''
# This file summarizes all warnings reported by the print_msg function

WORKSPACE = ''
# The Jenkins workspace directory

WORKSPACE_TOKENS: List[str] = []

XML_FILENAME = None
XML_DIR = ''
XML_BASENAME = ''
# Attributes of the Liquibase.xml file.
# XML_DIR + XML_BASENAME = XML_FILENAME

Z_FILE = ''
# That file holds the regular expressions for checking TERADATA_DDL
# files for expected content.
