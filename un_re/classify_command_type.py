# pylint: disable=C0209			# Don't require formatted strings
# pylint: disable=R0915			# Don't limit the number of tatements

# ===============================================================================
import re

import un_re.global_shared_variables as G
from un_re.get_file_contents import get_file_contents
from un_re.indent_info import indent_info
from un_re.remove_comments import remove_comments
from un_re.remove_sqlplus_prompts import remove_sqlplus_prompts
from un_re.split_antlr_line import split_antlr_line


# ===============================================================================
def populate_command_regexes_db2():
    G.COMMAND_REGEXES = {}

    G.COMMAND_REGEXES['^GRANT.*ON'] = "GRANT"

    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?\bADD\b'] = "ALTER TABLE COLUMN"

    G.COMMAND_REGEXES[r'^CREATE\s*.*TABLE.*\bAS\b.*\b(SELECT|SEL)\b.*\bFROM\b'] \
        = "CREATE TABLE AS SELECT"
    G.COMMAND_REGEXES[r'CREATE\s.*\bTABLE\b'] = "CREATE TABLE"
    G.COMMAND_REGEXES[r'CREATE\s*(UNIQUE|BITMAP|MULTIVALUE)?\s*INDEX\s+'] \
        = "CREATE INDEX"

    G.COMMAND_REGEXES[r'DROP\s*TABLE\b'] = "DROP TABLE"

    G.COMMAND_REGEXES[r'^SET\s+SCHEMA\b'] = "SET SCHEMA"


# ===============================================================================
def populate_command_regexes_redshift():
    G.COMMAND_REGEXES = {}

    G.COMMAND_REGEXES['^GRANT.*ON'] = "GRANT"

    G.COMMAND_REGEXES['COMMENT ON COLUMN'] = "COMMENT ON COLUMN"
    G.COMMAND_REGEXES['COMMENT ON TABLE'] = "COMMENT ON TABLE"

    G.COMMAND_REGEXES[r'^CREATE\s*.*TABLE.*\bAS\b.*\b(SELECT|SEL)\b.*\bFROM\b'] \
        = "CREATE TABLE AS SELECT"
    G.COMMAND_REGEXES[r'CREATE\s.*\bTABLE\b'] = "CREATE TABLE"
    G.COMMAND_REGEXES[r'^CREATE\s*VIEW'] = "CREATE VIEW"
    G.COMMAND_REGEXES[r'REPLACE\s*?\bVIEW\b'] = "CREATE VIEW"

    G.COMMAND_REGEXES[r'^INSERT|^INS\b'] = "INSERT"
    G.COMMAND_REGEXES[r'^(FROM|WITH)\b.*(INSERT|INS)\b'] = "INSERT"
    G.COMMAND_REGEXES[r'SELECT|SEL\b'] = "SELECT"

    G.COMMAND_REGEXES[r'^SET\s+.*?SEARCH_PATH'] = "DEFAULT DATABASE"
    G.COMMAND_REGEXES[r'^SET\s+'] = "SET"


# ===============================================================================
def populate_command_regexes_postgres():
    G.COMMAND_REGEXES = {}

    G.COMMAND_REGEXES['COMMENT ON COLUMN'] = "COMMENT ON COLUMN"
    G.COMMAND_REGEXES['COMMENT ON TABLE'] = "COMMENT ON TABLE"

    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?CONSTRAINT\b'] = "ALTER TABLE CONSTRAINT"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b.*?\bALTER\s+\bCOLUMN\b'] \
        = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?\bADD\b'] = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*OWNER\b'] = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b.*?RENAME\s.*\bTO\b'] \
        = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b'] = "ALTER TABLE OPTIONS"
    G.COMMAND_REGEXES[r'^ALTER\s*SEQUENCE'] = "ALTER SEQUENCE"
    G.COMMAND_REGEXES[r'^ALTER\s*SCHEMA'] = "ALTER SCHEMA"

    G.COMMAND_REGEXES[r'^CREATE\s*.*TABLE.*\bAS\b.*\b(SELECT|SEL)\b.*\bFROM\b'] \
        = "CREATE TABLE AS SELECT"
    G.COMMAND_REGEXES[r'CREATE\s.*\bTABLE\b'] = "CREATE TABLE"
    G.COMMAND_REGEXES[r'CREATE\s*.*\s*INDEX'] = "CREATE INDEX"
    G.COMMAND_REGEXES[r'CREATE\s+SEQUENCE'] = "CREATE SEQUENCE"
    G.COMMAND_REGEXES[r'CREATE\s.*\bUSER\b'] = "CREATE USER"
    G.COMMAND_REGEXES[r'^CREATE\s*DATABASE'] = "CREATE DATABASE"
    G.COMMAND_REGEXES['CREATE SCHEMA'] = "CREATE SCHEMA"
    G.COMMAND_REGEXES[r'CREATE\s*(OR\s*REPLACE)?\s*TYPE\b.*?(IS\b|AS\b)'] \
        = "CREATE TYPE"
    G.COMMAND_REGEXES[r'^CREATE\s*VIEW'] = "CREATE VIEW"
    G.COMMAND_REGEXES[r'^CREATE\s*RULE'] = "CREATE RULE"

    G.COMMAND_REGEXES[r'DROP\s*TABLE\b'] = "DROP TABLE"

    G.COMMAND_REGEXES[r'SELECT|SEL\b'] = "SELECT"

    G.COMMAND_REGEXES[r'^\\c'] = "CONNECT"
    G.COMMAND_REGEXES[r'^SET\s+'] = "SET"
    G.COMMAND_REGEXES[r'^COPY\b'] = "COPY"


# ===============================================================================
def populate_command_regexes_snowflake():
    G.COMMAND_REGEXES = {}

    G.COMMAND_REGEXES['^GRANT.*ON'] = "GRANT"
    G.COMMAND_REGEXES[r'^GRANT.*TO\s'] = "GRANT"

    G.COMMAND_REGEXES[r'^SET\s+'] = "SET"

    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*PROCEDURE'] = "CREATE PROCEDURE"
    G.COMMAND_REGEXES[r'CREATE\s*(OR\s*REPLACE)?\s*(EXTERNAL)?\s*FUNCTION\b'] \
        = "CREATE FUNCTION"

    G.COMMAND_REGEXES[r'^ALTER\s*SECURITY\s*INTEGRATION'] = "ALTER SECURITY INTEGRATION"
    G.COMMAND_REGEXES[r'^ALTER\s*ACCOUNT'] = "ALTER ACCOUNT"
    G.COMMAND_REGEXES[r'^ALTER\s*DATABASE'] = "ALTER DATABASE"
    G.COMMAND_REGEXES[r'ALTER\s*SESSION'] = "ALTER SESSION"

    G.COMMAND_REGEXES[r'^CREATE\s*.*TABLE.*\bAS\b.*\b(SELECT|SEL)\b.*\bFROM\b'] \
        = "CREATE TABLE AS SELECT"
    G.COMMAND_REGEXES[r'CREATE\s.*\bTABLE\b'] = "CREATE TABLE"

    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*WAREHOUSE'] = "CREATE WAREHOUSE"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*USER'] = "CREATE USER"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*ROLE'] = "CREATE ROLE"
    G.COMMAND_REGEXES[r'^CREATE\s*SECURITY\s*INTEGRATION'] = "CREATE SECURITY INTEGRATION"
    G.COMMAND_REGEXES[r'^CREATE\s*STORAGE\s*INTEGRATION'] = "CREATE STORAGE INTEGRATION"
    G.COMMAND_REGEXES['CREATE SCHEMA'] = "CREATE SCHEMA"
    G.COMMAND_REGEXES[r'^CREATE\s*TAG'] = "CREATE TAG"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*SESSION\s*POLICY\b'] \
        = "CREATE SESSION POLICY"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*NETWORK\s*POLICY\b'] \
        = "CREATE NETWORK POLICY"
    G.COMMAND_REGEXES[r'^CREATE\s*DATABASE'] = "CREATE DATABASE"
    G.COMMAND_REGEXES[r'^CREATE\s*API\s*INTEGRATION'] = "CREATE API INTEGRATION"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*ROW\s*ACCESS\s*POLICY\b'] \
        = "CREATE ROW ACCESS POLICY"
    G.COMMAND_REGEXES[r'^CREATE\s*VIEW'] = "CREATE VIEW"
    G.COMMAND_REGEXES[r'REPLACE\s*?\bVIEW\b'] = "CREATE VIEW"
    G.COMMAND_REGEXES[r'CREATE\s+SEQUENCE'] = "CREATE SEQUENCE"

    G.COMMAND_REGEXES[r'SELECT|SEL\b'] = "SELECT"

    G.COMMAND_REGEXES[r'DROP\s*PROCEDURE\b'] = "DROP PROCEDURE"
    G.COMMAND_REGEXES['DROP VIEW'] = "DROP VIEW"
    G.COMMAND_REGEXES[r'^DROP\s*FUNCTION'] = "DROP FUNCTION"

    G.COMMAND_REGEXES[r'^USE\s*ROLE\b'] = "USE ROLE"
    G.COMMAND_REGEXES[r'^USE\s*WAREHOUSE\b'] = "USE WAREHOUSE"
    G.COMMAND_REGEXES[r'^USE\s*'] = "DEFAULT DATABASE"

    G.COMMAND_REGEXES[r'^.*\(.*?\);'] = "CALL"
    # A name, followed by parameters in parentheses, terminating with semi-colon, must a procedure call
    # Procedure calls don't always have parentheses though, and there is no
    # way to distinguish them at compile time from references to variables
    # that could simply be dynamic SQL.

    G.COMMAND_REGEXES[r'^DESC\s*STORAGE\s*INTEGRATION'] = "DESCRIBE"
    G.COMMAND_REGEXES[r'^DESC\s*API\s*INTEGRATION'] = "DESCRIBE"
    G.COMMAND_REGEXES[r'^DESCRIBE\s'] = "DESCRIBE"
    G.COMMAND_REGEXES[r'^SHOW\s*'] = "SHOW"
    G.COMMAND_REGEXES['[a-z0-9]'] = "EMPTY FILE"


# ===============================================================================
def populate_command_regexes_hive():
    G.COMMAND_REGEXES = {}

    G.COMMAND_REGEXES[r'^SET\s+'] = "SET"

    G.COMMAND_REGEXES[r'^USE\s*'] = "DEFAULT DATABASE"

    G.COMMAND_REGEXES[r'CREATE\s*(TEMPORARY)?\s*FUNCTION\b.*?(AS\b)'] \
        = "CREATE FUNCTION"  # Hive version

    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?PARTITION'] = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?\bSET\b'] = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b.*?RENAME\s.*\bTO\b'] \
        = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*CHANGE\b'] = "ALTER TABLE COLUMN"

    G.COMMAND_REGEXES[r'^CREATE\s*.*TABLE.*\bAS\b.*\b(SELECT|SEL)\b.*\bFROM\b'] = "CREATE TABLE AS SELECT"
    G.COMMAND_REGEXES[r'CREATE\s.*\bTABLE\b'] = "CREATE TABLE"
    G.COMMAND_REGEXES[r'^CREATE\s*VIEW'] = "CREATE VIEW"

    G.COMMAND_REGEXES[r'DROP\s*TABLE\b'] = "DROP TABLE"
    G.COMMAND_REGEXES[r'^DROP VIEW'] = "DROP VIEW"

    G.COMMAND_REGEXES[r'^EXPLAIN\b'] = "EXPLAIN"
    G.COMMAND_REGEXES[r'^MERGE\s'] = "MERGE"
    G.COMMAND_REGEXES[r'^UPDATE|^UPD\b'] = "UPDATE"
    G.COMMAND_REGEXES[r'^INSERT|^INS\b'] = "INSERT"
    G.COMMAND_REGEXES[r'^(FROM|WITH)\b.*(INSERT|INS)\b'] = "INSERT"
    G.COMMAND_REGEXES[r'^DELETE\s|^DEL\s'] = "DELETE"
    G.COMMAND_REGEXES[r'SELECT|SEL\b'] = "SELECT"

    G.COMMAND_REGEXES[r'^ANALYZE\s*TABLE\b'] = "COLLECT STATISTICS"
    G.COMMAND_REGEXES[r'^INVALIDATE\s*METADATA'] = "INVALIDATE METADATA"
    G.COMMAND_REGEXES[r'^MSCK\s*REPAIR'] = "MSCK REPAIR"


# ===============================================================================
def populate_command_regexes_teradata():
    G.COMMAND_REGEXES = {}

    G.COMMAND_REGEXES[r'^\.OS'] = 'DOT OS'
    G.COMMAND_REGEXES[r'^\.COMPILE'] = 'DOT COMPILE'
    G.COMMAND_REGEXES[r'^\.IF'] = 'DOT IF'
    G.COMMAND_REGEXES[r'\.GOTO'] = "DOT GOTO"
    G.COMMAND_REGEXES[r'^\.LABEL'] = "LABEL"
    G.COMMAND_REGEXES[r'^\.SKIPLINE'] = "DOT SET"
    G.COMMAND_REGEXES['ACTIVITYCOUNT'] = "ACTIVITYCOUNT"
    G.COMMAND_REGEXES['WITH DATA AND STATS'] = "BACKUP TABLE"
    G.COMMAND_REGEXES['COMMENT ON COLUMN'] = "COMMENT ON COLUMN"
    G.COMMAND_REGEXES['COMMENT ON TABLE'] = "COMMENT ON TABLE"
    G.COMMAND_REGEXES['^GRANT.*ON'] = "GRANT"

    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?FOREIGN\b'] = "ALTER TABLE CONSTRAINT"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?\bADD\b'] = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b.*?RENAME\s.*\bTO\b'] = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*DROP\b'] = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b'] = "ALTER TABLE OPTIONS"

    G.COMMAND_REGEXES[r'^CREATE\s*.*TABLE.*\bAS\b.*\b(SELECT|SEL)\b.*\bFROM\b'] \
        = "CREATE TABLE AS SELECT"
    G.COMMAND_REGEXES[r'CREATE\s.*\bTABLE\b'] = "CREATE TABLE"
    G.COMMAND_REGEXES[r'^CREATE\s*VIEW'] = "CREATE VIEW"
    G.COMMAND_REGEXES[r'REPLACE\s*?\bVIEW\b'] = "CREATE VIEW"
    G.COMMAND_REGEXES[r'CREATE\s*.*\s*INDEX'] = "CREATE INDEX"
    G.COMMAND_REGEXES['RENAME TABLE'] = "RENAME TABLE"

    G.COMMAND_REGEXES[r'DROP\s*TABLE\b'] = "DROP TABLE"
    G.COMMAND_REGEXES[r'^DATABASE .*;'] = "DEFAULT DATABASE"

    G.COMMAND_REGEXES[r'^MERGE\s'] = "MERGE"
    G.COMMAND_REGEXES[r'^UPDATE|^UPD\b'] = "UPDATE"
    G.COMMAND_REGEXES[r'^INSERT|^INS\b'] = "INSERT"
    G.COMMAND_REGEXES[r'^(FROM|WITH)\b.*(INSERT|INS)\b'] = "INSERT"
    G.COMMAND_REGEXES[r'^DELETE\s|^DEL\s'] = "DELETE"
    G.COMMAND_REGEXES[r'SELECT|SEL\b'] = "SELECT"

    G.COMMAND_REGEXES['COLLECT (SUMMARY )?STAT'] = "COLLECT STATS"

    G.COMMAND_REGEXES[r'CREATE\s*(OR\s*REPLACE)?\s*(EDITIONABLE|NONEDITIONABLE)?\s*TYPE\b.*?(IS\b|AS\b)'] \
        = "CREATE TYPE"
    G.COMMAND_REGEXES[r'CALL\b.*\('] = "CALL"
    G.COMMAND_REGEXES[r'\.SET'] = "DOT SET"
    G.COMMAND_REGEXES[r'\.REMARK'] = 'DOT REMARK'
    G.COMMAND_REGEXES[r'\.QUIT'] = 'DOT QUIT'

    G.COMMAND_REGEXES['[a-z0-9]'] = "EMPTY FILE"


# ===============================================================================
def populate_command_regexes_databricks():
    G.COMMAND_REGEXES = {}

    G.COMMAND_REGEXES['COMMENT ON COLUMN'] = "COMMENT ON COLUMN"
    G.COMMAND_REGEXES['COMMENT ON TABLE'] = "COMMENT ON TABLE"

    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?CONSTRAINT\b'] = "ALTER TABLE CONSTRAINT"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b.*?\bALTER\s+\bCOLUMN\b.*?COMMENT\b'] \
        = "COMMENT ON COLUMN"  # for Databricks
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b.*?\bALTER\s+\bCOLUMN\b'] \
        = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?PARTITION'] = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?\bADD\b'] = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?\bSET\b'] = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?\bUNSET\b'] = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b.*?\bRENAME\s+\bCOLUMN\b'] \
        = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b.*?RENAME\s.*\bTO\b'] \
        = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*CHANGE\b'] = "ALTER TABLE COLUMN"

    G.COMMAND_REGEXES[r'^CREATE\s*BLOOMFILTER\s*INDEX'] = "CREATE INDEX"

    # G.COMMAND_REGEXES [r'^CREATE\s*.*TABLE.*\bAS\b.*\b(SELECT|SEL)\b.*\bFROM\b'] \
    # 								= "CREATE TABLE AS SELECT"
    G.COMMAND_REGEXES[r'^CREATE\s*.*TABLE.*?(\s)AS.*?SELECT\b'] \
        = "CREATE TABLE AS SELECT"
    G.COMMAND_REGEXES[r'^CREATE\s.*\bLIVE\s.*TABLE\b'] = "CREATE TABLE"
    # LIVE tables are used by Databricks
    G.COMMAND_REGEXES[r'CREATE\s.*\bTABLE\b'] = "CREATE TABLE"

    G.COMMAND_REGEXES[r'^CREATE\s*VIEW'] = "CREATE VIEW"
    G.COMMAND_REGEXES['CREATE SCHEMA'] = "CREATE SCHEMA"
    G.COMMAND_REGEXES[r'^CREATE\s*CATALOG'] = "CREATE CATALOG"

    G.COMMAND_REGEXES[r'REPLACE\s*?\bVIEW\b'] = "CREATE VIEW"

    G.COMMAND_REGEXES[r'DROP\s*TABLE\b'] = "DROP TABLE"

    G.COMMAND_REGEXES[r'^INSERT|^INS\b'] = "INSERT"
    G.COMMAND_REGEXES[r'^(FROM|WITH)\b.*(INSERT|INS)\b'] = "INSERT"
    G.COMMAND_REGEXES[r'SELECT\b'] = "SELECT"

    G.COMMAND_REGEXES[r'^OPTIMIZE\s*'] = "OPTIMIZE"
    G.COMMAND_REGEXES[r'^ANALYZE\s*TABLE\b'] = "COLLECT STATISTICS"
    G.COMMAND_REGEXES[r'^DESCRIBE\s'] = "DESCRIBE"

    G.COMMAND_REGEXES[r'^SHOW\s*'] = "SHOW"

    G.COMMAND_REGEXES[r'^USE\s*'] = "DEFAULT DATABASE"

    G.COMMAND_REGEXES[r'^COMMENT\s*ON\s*CATALOG\b'] = "COMMENT ON"
    G.COMMAND_REGEXES[r'^COMMENT\s*ON\s*CONNECTION\b'] = "COMMENT ON"
    G.COMMAND_REGEXES[r'^COMMENT\s*ON\s*SCHEMA\b'] = "COMMENT ON"
    G.COMMAND_REGEXES[r'^COMMENT\s*ON\s*RECIPIENT\b'] = "COMMENT ON"
    G.COMMAND_REGEXES[r'^COMMENT\s*ON\s*SHARE\b'] = "COMMENT ON"
    G.COMMAND_REGEXES[r'^COMMENT\s*ON\s*PROVIDER\b'] = "COMMENT ON"

    G.COMMAND_REGEXES[r'^VACUUM\s*'] = "VACUUM"


# ===============================================================================
def populate_command_regexes_ore():
    G.COMMAND_REGEXES = {}
    G.COMMAND_REGEXES[r'^NOAUDIT\s'] = "NOAUDIT"
    # Classify NOAUDIT first, because it can apply to most other command types.

    G.COMMAND_REGEXES['COMMENT ON COLUMN'] = "COMMENT ON COLUMN"

    G.COMMAND_REGEXES[r'^GRANT.*ON'] = "GRANT"
    G.COMMAND_REGEXES[r'^GRANT.*TO\s'] = "GRANT"

    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*PACKAGE\s*BODY'] = "CREATE PACKAGE BODY"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*PACKAGE\b'] = "CREATE PACKAGE"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*PROCEDURE'] = "CREATE PROCEDURE"
    G.COMMAND_REGEXES[r'CREATE\s.*TRIGGER\b'] = "CREATE TRIGGER"

    G.COMMAND_REGEXES[r'CREATE\s.*\bTYPE\b\s*BODY\s.*(IS\b|AS\b)'] \
        = "CREATE TYPE BODY"
    G.COMMAND_REGEXES[r'CREATE\s*(OR\s*REPLACE)?\s*(EDITIONABLE|NONEDITIONABLE)?\s*TYPE\b.*?(IS\b|AS\b)'] \
        = "CREATE TYPE"
    G.COMMAND_REGEXES[r'CREATE\s*(OR\s*REPLACE)?\s*(EDITIONABLE|NONEDITIONABLE)?\s*FUNCTION\b.*?(IS\b|AS\b)'] \
        = "CREATE FUNCTION"

    G.COMMAND_REGEXES[r'^(DECLARE|BEGIN).*/'] = "PLSQL BLOCK"

    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?CONSTRAINT\b'] = "ALTER TABLE CONSTRAINT"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?FOREIGN\b'] = "ALTER TABLE CONSTRAINT"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?PRIMARY'] = "ALTER TABLE CONSTRAINT"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?CHECK\b'] = "ALTER TABLE CONSTRAINT"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?PARTITION'] = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?\bADD\b'] = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b.*?RENAME\s.*\bTO\b'] \
        = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*MODIFY\b'] = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*DROP\b'] = "ALTER TABLE COLUMN"

    G.COMMAND_REGEXES[r'CREATE\s+MATERIALIZED\s+VIEW'] = "CREATE MATERIALIZED VIEW"
    # Check Mat Views before indexes, because Mat views can specify no index

    G.COMMAND_REGEXES[r'CREATE\s*.*\s*INDEX'] = "CREATE INDEX"
    G.COMMAND_REGEXES[r'^CREATE\s*.*TABLE.*\bAS\b.*\b(SELECT|SEL)\b.*\bFROM\b'] = "CREATE TABLE AS SELECT"
    G.COMMAND_REGEXES[r'CREATE\s.*\bTABLE\b'] = "CREATE TABLE"
    G.COMMAND_REGEXES[r'CREATE\s+SEQUENCE'] = "CREATE SEQUENCE"

    G.COMMAND_REGEXES[r'MERGE\s'] = "MERGE"
    G.COMMAND_REGEXES[r'DROP\s*INDEX'] = "DROP INDEX"
    G.COMMAND_REGEXES[r'DROP\s*TABLE\b'] = "DROP TABLE"

    G.COMMAND_REGEXES[r'ALTER\s*USER\b'] = "ALTER USER"
    G.COMMAND_REGEXES[r'CREATE\s.*\bUSER\b'] = "CREATE USER"

    G.COMMAND_REGEXES['DROP VIEW'] = "DROP VIEW"

    G.COMMAND_REGEXES[r'(EXEC|EXECUTE)\s'] = "EXEC"
    G.COMMAND_REGEXES[r'COMMIT'] = "COMMIT"
    G.COMMAND_REGEXES[r'^UPDATE\b'] = "UPDATE"
    G.COMMAND_REGEXES[r'^INSERT\b'] = "INSERT"
    G.COMMAND_REGEXES[r'^(FROM|WITH)\b.*INSERT\b'] = "INSERT"
    G.COMMAND_REGEXES[r'^DELETE\s|^DEL\s'] = "DELETE"
    G.COMMAND_REGEXES[r'SELECT|SEL\b'] = "SELECT"

    G.COMMAND_REGEXES[r'CREATE\s.*?SYNONYM'] = "CREATE SYNONYM"
    G.COMMAND_REGEXES[r'SET\s+SERVEROUTPUT'] = "SQLPLUS"
    G.COMMAND_REGEXES[r'^SET\s+'] = "SET"
    # G.COMMAND_REGEXES [r'SET\s.*ECHO']                         	= "SQLPLUS"
    G.COMMAND_REGEXES[r'^WHENEVER\s+SQLERROR'] = "SQLPLUS"
    G.COMMAND_REGEXES[r'SHOW\s*ERRORS'] = "SQLPLUS"
    G.COMMAND_REGEXES[r'SPOOL'] = "SQLPLUS"
    G.COMMAND_REGEXES[r'SET\s+DEFINE'] = "SQLPLUS"

    G.COMMAND_REGEXES[r'^/$'] = 'UNNECESSARY SLASH'

    G.COMMAND_REGEXES[r'ALTER\s*INDEX'] = "ALTER INDEX"

    G.COMMAND_REGEXES[r'CREATE\s.*\bTABLESPACE\b'] = "CREATE TABLESPACE"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*ROLE'] = "CREATE ROLE"
    G.COMMAND_REGEXES[r'DROP\s*TABLESPACE\s*SET\b'] = "DROP TABLESPACE SET"
    G.COMMAND_REGEXES[r'DROP\s*TABLESPACE\b'] = "DROP TABLESPACE"
    G.COMMAND_REGEXES[r'DROP\s*DATABASE\b'] = "DROP DATABASE"
    G.COMMAND_REGEXES[r'DROP\s*ROLLBACK\s*SEGMENT\b'] = "DROP ROLLBACK SEGMENT"
    G.COMMAND_REGEXES[r'DROP\s*USER\b'] = "DROP USER"
    G.COMMAND_REGEXES[r'DROP\s*FLASHBACK\s*ARCHIVE\b'] = "DROP FLASHBACK ARCHIVE"
    G.COMMAND_REGEXES[r'DROP\s*DISKGROUP\b'] = "DROP DISKGROUP"
    G.COMMAND_REGEXES[r'DROP\s*PMEM\s*FILESTORE\b'] = "DROP PMEM FILESTORE"
    G.COMMAND_REGEXES[r'DROP\s+MATERIALIZED\s+VIEW'] = "DROP MATERIALIZED VIEW"
    G.COMMAND_REGEXES[r'COMMENT\s+ON\s+MATERIALIZED\s+VIEW'] = "COMMENT ON MATERIALIZED VIEW"
    G.COMMAND_REGEXES[r'DROP\s*TYPE'] = "DROP TYPE"

    G.COMMAND_REGEXES[r'CALL\b.*\('] = "CALL"

    G.COMMAND_REGEXES[r'TRUNCATE\s+TABLE'] = "TRUNCATE TABLE"
    G.COMMAND_REGEXES[r'^PURGE\s'] = "PURGE"
    G.COMMAND_REGEXES[r'FLASHBACK\s*(STANDBY)?\s*(PLUGGABLE)?\s*DATABASE\b'] \
        = "FLASHBACK DATABASE"
    G.COMMAND_REGEXES[r'FLASHBACK\s*TABLE\b'] = "FLASHBACK TABLE"

    G.COMMAND_REGEXES[r'^.*\(.*?\);'] = "CALL"
    G.COMMAND_REGEXES['[a-z0-9]'] = "EMPTY FILE"


# ===============================================================================
def populate_command_regexes_other():
    G.COMMAND_REGEXES = {}
    G.COMMAND_REGEXES[r'^NOAUDIT\s'] = "NOAUDIT"
    # Classify NOAUDIT first, because it can apply to most other command types.

    G.COMMAND_REGEXES[r'^\.OS'] = 'DOT OS'
    G.COMMAND_REGEXES[r'^\.COMPILE'] = 'DOT COMPILE'
    G.COMMAND_REGEXES[r'^\.IF'] = 'DOT IF'
    G.COMMAND_REGEXES[r'\.GOTO'] = "DOT GOTO"
    G.COMMAND_REGEXES[r'^\.LABEL'] = "LABEL"
    G.COMMAND_REGEXES[r'^\.SKIPLINE'] = "DOT SET"
    G.COMMAND_REGEXES['ACTIVITYCOUNT'] = "ACTIVITYCOUNT"
    G.COMMAND_REGEXES['WITH DATA AND STATS'] = "BACKUP TABLE"
    G.COMMAND_REGEXES['COMMENT ON COLUMN'] = "COMMENT ON COLUMN"
    G.COMMAND_REGEXES['COMMENT ON TABLE'] = "COMMENT ON TABLE"
    G.COMMAND_REGEXES['^GRANT.*ON'] = "GRANT"
    G.COMMAND_REGEXES[r'^GRANT.*TO\s'] = "GRANT"

    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*PACKAGE\s*BODY'] = "CREATE PACKAGE BODY"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*PACKAGE\b'] = "CREATE PACKAGE"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*PROCEDURE'] = "CREATE PROCEDURE"
    G.COMMAND_REGEXES[r'CREATE\s.*TRIGGER\b'] = "CREATE TRIGGER"
    # Check triggers before types, because triggers can use types

    G.COMMAND_REGEXES[r'CREATE\s.*\bTYPE\b\s*BODY\s.*(IS\b|AS\b)'] \
        = "CREATE TYPE BODY"
    G.COMMAND_REGEXES[r'CREATE\s*(OR\s*REPLACE)?\s*(EDITIONABLE|NONEDITIONABLE)?\s*TYPE\b.*?(IS\b|AS\b)'] \
        = "CREATE TYPE"

    G.COMMAND_REGEXES[r'CREATE\s*(OR\s*REPLACE)?\s*(EDITIONABLE|NONEDITIONABLE)?\s*FUNCTION\b.*?(IS\b|AS\b)'] \
        = "CREATE FUNCTION"
    G.COMMAND_REGEXES[r'CREATE\s*(OR\s*REPLACE)?\s*(EXTERNAL)?\s*FUNCTION\b'] \
        = "CREATE FUNCTION"
    G.COMMAND_REGEXES[r'CREATE\s*(TEMPORARY)?\s*FUNCTION\b.*?(AS\b)'] \
        = "CREATE FUNCTION"  # Hive version

    G.COMMAND_REGEXES[r'^(DECLARE|BEGIN).*/'] = "PLSQL BLOCK"

    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?CONSTRAINT\b'] = "ALTER TABLE CONSTRAINT"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?FOREIGN\b'] = "ALTER TABLE CONSTRAINT"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?PRIMARY'] = "ALTER TABLE CONSTRAINT"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?CHECK\b'] = "ALTER TABLE CONSTRAINT"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b.*?\bALTER\s+\bCOLUMN\b.*?COMMENT\b'] \
        = "COMMENT ON COLUMN"  # for Databricks
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b.*?\bALTER\s+\bCOLUMN\b'] \
        = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?PARTITION'] = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?\bADD\b'] = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?\bSET\b'] = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*?\bUNSET\b'] = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*OWNER\b'] = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b.*?\bRENAME\s+\bCOLUMN\b'] \
        = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b.*?RENAME\s.*\bTO\b'] \
        = "ALTER TABLE OTHER"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*CHANGE\b'] = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*MODIFY\b'] = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\s+.*?TABLE\s.*DROP\b'] = "ALTER TABLE COLUMN"
    G.COMMAND_REGEXES[r'^ALTER\b.*\bTABLE\b'] = "ALTER TABLE OPTIONS"

    G.COMMAND_REGEXES[r'CREATE\s+MATERIALIZED\s+VIEW'] = "CREATE MATERIALIZED VIEW"
    # Check Mat Views before indexes, because Mat views can specify no index

    G.COMMAND_REGEXES[r'^CREATE\s*BLOOMFILTER\s*INDEX'] = "CREATE INDEX"
    G.COMMAND_REGEXES[r'^CREATE\s.*\bLIVE\s.*TABLE\b'] = "CREATE TABLE"
    # LIVE tables are used by Databricks
    G.COMMAND_REGEXES[r'^CREATE\s*.*TABLE.*\bAS\b.*\b(SELECT|SEL)\b.*\bFROM\b'] = "CREATE TABLE AS SELECT"
    G.COMMAND_REGEXES[r'CREATE\s.*\bTABLE\b'] = "CREATE TABLE"
    G.COMMAND_REGEXES[r'ALTER\s+VIEW'] = "ALTER VIEW"

    G.COMMAND_REGEXES[r'CREATE\s*(UNIQUE|BITMAP|MULTIVALUE)?\s*INDEX\s+'] \
        = "CREATE INDEX"
    G.COMMAND_REGEXES[r'CREATE\s*.*\s*INDEX'] = "CREATE INDEX"

    G.COMMAND_REGEXES[r'ALTER\s+VIEW'] = "ALTER VIEW"
    G.COMMAND_REGEXES['COMMIT'] = "COMMIT"

    G.COMMAND_REGEXES[r'^CREATE\s*VIEW'] = "CREATE VIEW"
    G.COMMAND_REGEXES[r'MERGE\s'] = "MERGE"
    G.COMMAND_REGEXES[r'DROP\s*INDEX'] = "DROP INDEX"
    G.COMMAND_REGEXES[r'DROP\s*TABLE\b'] = "DROP TABLE"

    G.COMMAND_REGEXES['DROP VIEW'] = "DROP VIEW"
    G.COMMAND_REGEXES[r'(EXEC|EXECUTE)\s'] = "EXEC"
    G.COMMAND_REGEXES['RENAME TABLE'] = "RENAME TABLE"

    G.COMMAND_REGEXES[r'REPLACE\s*?\bVIEW\b'] = "CREATE VIEW"

    G.COMMAND_REGEXES[r'^EXPLAIN\b'] = "EXPLAIN"
    G.COMMAND_REGEXES[r'^UPDATE|^UPD\b'] = "UPDATE"
    G.COMMAND_REGEXES[r'^INSERT|^INS\b'] = "INSERT"
    G.COMMAND_REGEXES[r'^(FROM|WITH)\b.*(INSERT|INS)\b'] = "INSERT"
    G.COMMAND_REGEXES[r'^DELETE\s|^DEL\s'] = "DELETE"

    G.COMMAND_REGEXES[r'^DATABASE .*;'] = "DEFAULT DATABASE"
    G.COMMAND_REGEXES[r'CREATE\s+SEQUENCE'] = "CREATE SEQUENCE"
    G.COMMAND_REGEXES[r'SET\s+SERVEROUTPUT'] = "SQLPLUS"
    G.COMMAND_REGEXES[r'^SET\s+SCHEMA\b'] = "SET SCHEMA"
    G.COMMAND_REGEXES[r'^SET\s+.*?SEARCH_PATH'] = "DEFAULT DATABASE"
    G.COMMAND_REGEXES[r'^SET\s+'] = "SET"
    G.COMMAND_REGEXES[r'TRUNCATE\s+TABLE'] = "TRUNCATE TABLE"
    G.COMMAND_REGEXES[r'SELECT|SEL\b'] = "SELECT"
    G.COMMAND_REGEXES[r'WHENEVER\s+SQLERROR'] = "SQLPLUS"
    G.COMMAND_REGEXES[r'^/$'] = 'UNNECESSARY SLASH'
    G.COMMAND_REGEXES[r'DROP\s+MATERIALIZED\s+VIEW'] = "DROP MATERIALIZED VIEW"
    G.COMMAND_REGEXES[r'COMMENT\s+ON\s+MATERIALIZED\s+VIEW'] = "COMMENT ON MATERIALIZED VIEW"
    G.COMMAND_REGEXES[r'DROP\s*TYPE'] = "DROP TYPE"

    G.COMMAND_REGEXES[r'CALL\b.*\('] = "CALL"

    G.COMMAND_REGEXES[r'ALTER\s.*TRIGGER'] = "ALTER TRIGGER"
    G.COMMAND_REGEXES[r'SHOW\s*ERRORS'] = "SQLPLUS"
    G.COMMAND_REGEXES[r'DROP\s*TRIGGER'] = "DROP TRIGGER"
    G.COMMAND_REGEXES['REVOKE.*FROM'] = "REVOKE"
    G.COMMAND_REGEXES[r'DROP\s*PACKAGE\s*BODY'] = "DROP PACKAGE BODY"
    G.COMMAND_REGEXES[r'DROP\s*SEQUENCE'] = "DROP SEQUENCE"
    G.COMMAND_REGEXES[r'ALTER\s*INDEX'] = "ALTER INDEX"

    G.COMMAND_REGEXES['SPOOL'] = "SQLPLUS"
    G.COMMAND_REGEXES[r'SET\s+DEFINE'] = "SQLPLUS"
    G.COMMAND_REGEXES[r'CREATE\s.*DIRECTORY'] = "CREATE DIRECTORY"
    G.COMMAND_REGEXES[r'ALTER\s*SESSION'] = "ALTER SESSION"
    G.COMMAND_REGEXES[r'ALTER\s*USER\b'] = "ALTER USER"
    G.COMMAND_REGEXES[r'CREATE\s.*\bUSER\b'] = "CREATE USER"
    G.COMMAND_REGEXES[r'CREATE\s.*\bTABLESPACE\b'] = "CREATE TABLESPACE"
    G.COMMAND_REGEXES[r'DROP\s*PROCEDURE\b'] = "DROP PROCEDURE"
    G.COMMAND_REGEXES[r'DROP\s*(PUBLIC)?\s*SYNONYM\b'] = "DROP SYNONYM"
    G.COMMAND_REGEXES[r'DROP\s*DATABASE\b'] = "DROP DATABASE"
    G.COMMAND_REGEXES[r'DROP\s*DISKGROUP\b'] = "DROP DISKGROUP"
    G.COMMAND_REGEXES[r'DROP\s*FLASHBACK\s*ARCHIVE\b'] = "DROP FLASHBACK ARCHIVE"
    G.COMMAND_REGEXES[r'DROP\s*PMEM\s*FILESTORE\b'] = "DROP PMEM FILESTORE"
    G.COMMAND_REGEXES[r'DROP\s*ROLLBACK\s*SEGMENT\b'] = "DROP ROLLBACK SEGMENT"
    G.COMMAND_REGEXES[r'DROP\s*TABLESPACE\s*SET\b'] = "DROP TABLESPACE SET"
    G.COMMAND_REGEXES[r'DROP\s*TABLESPACE\b'] = "DROP TABLESPACE"
    G.COMMAND_REGEXES[r'DROP\s*USER\b'] = "DROP USER"
    G.COMMAND_REGEXES[r'FLASHBACK\s*(STANDBY)?\s*(PLUGGABLE)?\s*DATABASE\b'] \
        = "FLASHBACK DATABASE"
    G.COMMAND_REGEXES[r'FLASHBACK\s*TABLE\b'] = "FLASHBACK TABLE"
    G.COMMAND_REGEXES[r'^PURGE\s'] = "PURGE"

    G.COMMAND_REGEXES['COLLECT (SUMMARY )?STAT'] = "COLLECT STATS"
    G.COMMAND_REGEXES[r'\.SET'] = "DOT SET"
    G.COMMAND_REGEXES[r'\.REMARK'] = 'DOT REMARK'
    G.COMMAND_REGEXES[r'\.QUIT'] = 'DOT QUIT'
    G.COMMAND_REGEXES['CREATE SCHEMA'] = "CREATE SCHEMA"
    G.COMMAND_REGEXES[r'DROP\s*STAT'] = "DROP STATS"
    G.COMMAND_REGEXES[r'^ANALYZE\s*TABLE\b'] = "COLLECT STATISTICS"
    G.COMMAND_REGEXES[r'^USE\s*ROLE\b'] = "USE ROLE"
    G.COMMAND_REGEXES[r'^USE\s*WAREHOUSE\b'] = "USE WAREHOUSE"
    G.COMMAND_REGEXES[r'^USE\s*'] = "DEFAULT DATABASE"
    G.COMMAND_REGEXES[r'^INVALIDATE\s*METADATA'] = "INVALIDATE METADATA"
    G.COMMAND_REGEXES[r'^MSCK\s*REPAIR'] = "MSCK REPAIR"
    G.COMMAND_REGEXES[r'^CREATE\s*DATABASE'] = "CREATE DATABASE"
    G.COMMAND_REGEXES[r'^ALTER\s*SEQUENCE'] = "ALTER SEQUENCE"
    G.COMMAND_REGEXES[r'^ALTER\s*SCHEMA'] = "ALTER SCHEMA"
    G.COMMAND_REGEXES[r'^\\c'] = "CONNECT"
    G.COMMAND_REGEXES[r'^CREATE\s*RULE'] = "CREATE RULE"
    G.COMMAND_REGEXES[r'^COPY\b'] = "COPY"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*ROW\s*ACCESS\s*POLICY\b'] = "CREATE ROW ACCESS POLICY"
    G.COMMAND_REGEXES[r'^DROP\s*FUNCTION'] = "DROP FUNCTION"
    G.COMMAND_REGEXES[r'^OPTIMIZE\s*'] = "OPTIMIZE"
    G.COMMAND_REGEXES[r'^.*\(.*?\);'] = "CALL"
    # A name, followed by parameters in parentheses, terminating with semi-colon, must a procedure call
    # Procedure calls don't always have parentheses though, and there is no
    # way to distinguish them at compile time from references to variables
    # that could simply be dynamic SQL.
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*WAREHOUSE'] = "CREATE WAREHOUSE"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*USER'] = "CREATE USER"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*ROLE'] = "CREATE ROLE"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*SESSION\s*POLICY\b'] = "CREATE SESSION POLICY"
    G.COMMAND_REGEXES[r'^CREATE\s*(OR\s*REPLACE)?\s*NETWORK\s*POLICY\b'] = "CREATE NETWORK POLICY"
    G.COMMAND_REGEXES[r'^CREATE\s*SECURITY\s*INTEGRATION'] = "CREATE SECURITY INTEGRATION"
    G.COMMAND_REGEXES[r'^CREATE\s*STORAGE\s*INTEGRATION'] = "CREATE STORAGE INTEGRATION"
    G.COMMAND_REGEXES[r'^DESC\s*STORAGE\s*INTEGRATION'] = "DESCRIBE"
    G.COMMAND_REGEXES[r'^DESC\s*API\s*INTEGRATION'] = "DESCRIBE"
    G.COMMAND_REGEXES[r'^DESCRIBE\s'] = "DESCRIBE"
    G.COMMAND_REGEXES[r'^CREATE\s*API\s*INTEGRATION'] = "CREATE API INTEGRATION"
    G.COMMAND_REGEXES[r'^ALTER\s*SECURITY\s*INTEGRATION'] = "ALTER SECURITY INTEGRATION"
    G.COMMAND_REGEXES[r'^ALTER\s*ACCOUNT'] = "ALTER ACCOUNT"
    G.COMMAND_REGEXES[r'^ALTER\s*DATABASE'] = "ALTER DATABASE"
    G.COMMAND_REGEXES[r'^CREATE\s*TAG'] = "CREATE TAG"
    G.COMMAND_REGEXES[r'^SHOW\s*'] = "SHOW"
    G.COMMAND_REGEXES[r'^CREATE\s*CATALOG'] = "CREATE CATALOG"
    G.COMMAND_REGEXES[r'^COMMENT\s*ON\s*CATALOG\b'] = "COMMENT ON"
    G.COMMAND_REGEXES[r'^COMMENT\s*ON\s*CONNECTION\b'] = "COMMENT ON"
    G.COMMAND_REGEXES[r'^COMMENT\s*ON\s*SCHEMA\b'] = "COMMENT ON"
    G.COMMAND_REGEXES[r'^COMMENT\s*ON\s*RECIPIENT\b'] = "COMMENT ON"
    G.COMMAND_REGEXES[r'^COMMENT\s*ON\s*SHARE\b'] = "COMMENT ON"
    G.COMMAND_REGEXES[r'^COMMENT\s*ON\s*PROVIDER\b'] = "COMMENT ON"
    G.COMMAND_REGEXES['[a-z0-9]'] = "EMPTY FILE"


# ===============================================================================
def populate_command_regexes():
    """
    This function is called by the load_configuration_files module

    We have a LOT of these, and it has become unreasonable to create one
    list that is a superset of commands from all languages.

    We will have to create a separate list for each language.
    """

    if G.RULES_ENGINE_TYPE in ('TERADATA_DDL', 'TERADATA_DML', 'DATAOPS_TDV_DDL'):
        populate_command_regexes_teradata()
    elif G.RULES_ENGINE_TYPE == 'HIVE_DDL_RE':
        populate_command_regexes_hive()
    elif G.RULES_ENGINE_TYPE == 'DATABRICKS':
        populate_command_regexes_databricks()
    elif G.RULES_ENGINE_TYPE == 'SNOWFLAKE':
        populate_command_regexes_snowflake()
    elif G.RULES_ENGINE_TYPE == 'ORE':
        populate_command_regexes_ore()
    elif G.RULES_ENGINE_TYPE == 'PG_RE':
        populate_command_regexes_postgres()
    elif G.RULES_ENGINE_TYPE == 'REDSHIFT':
        populate_command_regexes_redshift()
    elif G.RULES_ENGINE_TYPE == 'DB2_RE':
        populate_command_regexes_db2()


# else:
# populate_command_regexes_other ()


# ===============================================================================
def classify_clean_statement_with_regex(statement):
    tentative_command_type = 'UNKNOWN'

    for regex, command_type in G.COMMAND_REGEXES.items():
        if re.search(regex, statement, re.IGNORECASE | re.DOTALL | re.MULTILINE):
            tentative_command_type = command_type
            break

    return tentative_command_type


# ===============================================================================
def classify_statement_with_regex(sql_stmt_txt):
    clean_contents = remove_comments(sql_stmt_txt)

    if G.RULES_ENGINE_TYPE == 'ORE':
        clean_contents = remove_sqlplus_prompts(clean_contents)

    clean_contents = clean_contents.replace('\n', ' ').replace('\r', '')

    G.TENTATIVE_COMMAND_TYPE = classify_clean_statement_with_regex(clean_contents)

    return G.TENTATIVE_COMMAND_TYPE


# ===============================================================================
def classify_file_contents_with_regex(statement):
    # global COMMAND_REGEXES   Is assigned above

    G.COMMAND_TYPE = 'UNKNOWN'

    for regex, command_type in G.COMMAND_REGEXES.items():
        try:
            if re.search(regex, statement, re.IGNORECASE | re.DOTALL | re.MULTILINE):
                G.COMMAND_TYPE = command_type
                break
        except:
            print(f'Failed to parse regex: {regex}')
            raise

    if G.COMMAND_TYPE == 'UNKNOWN':
        indent_info(f'WARNING-g005 : Unknown command: {statement[:30]}...')
    # indent_info (f'Reported from {os.path.basename (__file__)}')

    return G.COMMAND_TYPE


# ===============================================================================
def classify_input_filename_with_regex(input_filename):
    file_contents = remove_comments(get_file_contents(input_filename))
    file_contents = file_contents.replace('\n', ' ').replace('\r', '')

    classify_file_contents_with_regex(file_contents)


# ===============================================================================
def classify_input_filename_command_type(input_filename):
    """
    This function reads the input_filename that should contain 1 and only 1
    SQL or DDL command, and sets G.COMMAND_TYPE to identify what kind of
    command it is.

    This is valuable to the Rules Engine, because different commands are
    checked with different rules.
    """

    G.COMMAND_TYPE = ''

    for line in G.ANTLR_LOG_CONTENTS.split('\n'):
        if line.find('Statement Type               :') > -1:
            G.COMMAND_TYPE = split_antlr_line(line)
            G.COMMAND_TYPE = G.COMMAND_TYPE.strip()
        # break
        # Unfortunately, we can NOT break, because we need
        # to take the last command type, not the first, for cases
        # when a DDL command is part of DOT IF command

    if G.COMMAND_TYPE == '':
        # If Antlr didn't classify the command type, see if
        # we can classify the command type with a regex search
        G.LOGGER.debug((' ' * 15) + 'Notice       : Did not find command type in the Antlr log contents.')
        classify_input_filename_with_regex(input_filename)

    return G.COMMAND_TYPE


# ===============================================================================
def classify_input_statement_command_type(sql_stmt_obj):
    """
    This function reads the input sql_stmt_obj structure.
    It sets G.COMMAND_TYPE to identify what kind of command it is.

    This is valuable to the Rules Engine, because different commands are
    checked with different rules.

    Notice there are TWO ways to classify a command type.   Antlr would
    provide the most accurate classification, so give first preference to
    checking the ANTLR_LOG_CONTENTS.   But if it is not there, an
    alternative method would be to use the regex search helper function
    above.
    """

    G.COMMAND_TYPE = ''

    for line in sql_stmt_obj.antlr_log_contents.split('\n'):
        if line.find('Statement Type               :') > -1:
            G.COMMAND_TYPE = split_antlr_line(line)
            G.COMMAND_TYPE = G.COMMAND_TYPE.strip()
        # break
        # Unfortunately, we can NOT break, because we need
        # to take the last command type, not the first, for cases
        # when a DDL command is part of DOT IF command

    if G.COMMAND_TYPE == '':
        # If Antlr didn't classify the command type, see if
        # we can classify the command type with a regex search
        indent_info('WARNING-g005 : Did not find command type in the Antlr log contents.')
        G.COMMAND_TYPE = classify_statement_with_regex(sql_stmt_obj.sql_stmt_txt)

    sql_stmt_obj.command_type = G.COMMAND_TYPE

    return G.COMMAND_TYPE
