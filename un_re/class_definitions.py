# pylint: disable=C0209           	# Don't require formtted strings
# pylint: disable=C0302			# Too many lines in module
# pylint: disable=R0902			# Too many attributes
# pylint: disable=R0903			# Too few public methods
# pylint: disable=R0913			# Too many arguments

import os
import re
import textwrap
from typing import List

from un_re.class_definitions_base import Table_Extrt


# import  un_re.global_shared_vars        as G
# Please do not import any globals into these definitions, because they
# interfere with type checking.
# And don't import any function that import any globals, because it will create
# a circular import.
# We want to type-check if the globals use the classes right.  But if the
# classes need the globals and the globals need the classes, it becomes
# circular and doesn't work.


# ===============================================================================
# For advice about sorting classes, see:
# https://docs.python.org/3/howto/sorting.html
# https://stackoverflow.com/questions/4010322/sort-a-list-of-class-instances-python

class Abbreviation:
    cfg_filename_rel = 'un_re/resources/cfg_Enterprise_Naming_Standards.lst'

    def __init__(self, word, abbr):
        self.word = word.lower()
        self.abbr = abbr
        self.word_len = len(word)
        self.abbr_len = len(abbr)
        if word.find(' ') > -1:
            self.isa_multi_token_abbreviation = True
            self.search_phrase = self.word + r'\b'
        # Add \b to search on word boundary, i.e. whole words.
        else:
            self.isa_multi_token_abbreviation = False
            self.search_phrase = None

    def __lt__(self, other):
        # Sort by length-descending first,
        # then alphabetically
        if self.word_len == other.word_len:
            is_lt = self.word < other.word
        else:
            is_lt = self.word_len > other.word_len
        # Compare greather than to make it descending

        return is_lt

    def __eq__(self, other):
        # If the words are the same, they also have the same length
        return self.word == other.word

    def __hash__(self):
        return hash(self.word)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


class AbbreviatedMultiToken:
    # All abbreviations here should include an embedded space
    # Rule 303 can only search for these linearly, not with a
    # binary search
    def __init__(self, phrase, abbreviated_phrase):
        self.phrase = phrase.lower()
        self.abbreviated_phrase = abbreviated_phrase
        self.phrase_len = len(phrase)
        self.abbreviated_phrase_len = len(abbreviated_phrase)
        self.search_phrase = self.phrase + r'\b'

    def __lt__(self, other):
        # Sort by length-descending first,
        # then alphabetically
        if self.phrase_len == other.phrase_len:
            is_lt = self.phrase < other.phrase
        else:
            is_lt = self.phrase_len > other.phrase_len
        # Compare greather than to make it descending

        return is_lt

    def __eq__(self, other):
        # If the phrases are the same, they also have the same length
        return self.phrase == other.phrase

    def __hash__(self):
        return hash(self.phrase)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


class AbbreviatedSingleToken:
    # All abbreviations here should not have an embedded space
    # Rule 303 can use a binary search for these, so they
    # don't need a search-phrase attribute.
    def __init__(self, word, abbr):
        self.word = word.lower()
        self.abbr = abbr
        self.word_len = len(word)
        self.abbr_len = len(abbr)

    def __lt__(self, other):
        return self.word < other.word

    def __eq__(self, other):
        return self.word == other.word

    def __hash__(self):
        return hash(self.word)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class AntlrAttributes:

    def __init__(self, file_obj):
        self.statement_type = None
        self.database_base = 'UNKNOWN'
        self.table_name = None
        self.file_obj = file_obj
        self.sql_stmt_txt = ''
        self.column_descriptors = []
        # Each Column descriptors should be an AntlrColumn

        self.read_sql_stmt_txt = False
        # SQL statements often use multiple lines.  There are Antlr
        # actions to mark when the text of the statement will start
        # and stop.

        self.primary_key_is_specified = False

        self.tentative_command_type = 'UNKNOWN'
        self.table_comment = None

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += '{0}\n'.format(
            self.__class__.__name__)

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += '{0:24s}: {1}\n'.format(
                k,
                v)
        return line


# ===============================================================================
class AntlrColumn:

    def __init__(self, column_name):
        self.column_name = column_name
        self.datatype = None
        self.comment_txt = None
        self.is_identity = False

        self.naming_method: str = ''
        self.column_name_tokens: List[str] = []

        self.naming_method = None
        self.column_name_tokens = []

        self.classword = ''

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += '{0}\n'.format(
            self.__class__.__name__)

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += '{0:24s}: {1}\n'.format(
                k,
                v)
        return line


# ===============================================================================
class ArrayException:
    cfg_filename_rel = 'un_re/resources/cfg_array_exceptions.lst'

    def __init__(self, column_nm, expiration_dt, comment_txt):
        self.column_nm = column_nm
        self.expiration_dt = expiration_dt
        self.comment_txt = comment_txt

    def __lt__(self, other):
        return self.column_nm < other.column_nm

    def __eq__(self, other):
        return self.column_nm == other.column_nm

    def __hash__(self):
        return hash(self.column_nm)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class Article:
    cfg_filename_rel = 'un_re/resources/cfg_articles.lst'

    def __init__(self, article_nm):
        self.article_nm = article_nm

    def __lt__(self, other):
        return self.article_nm < other.article_nm

    def __eq__(self, other):
        return self.article_nm == other.article_nm

    def __hash__(self):
        return hash(self.article_nm)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class BusinessTerm:
    cfg_filename_rel = 'un_re/resources/cfg_business_terms.lst'

    def __init__(self, old_term_txt, new_term_txt, comment_txt):
        self.old_term_txt = old_term_txt
        self.new_term_txt = new_term_txt
        self.comment_txt = comment_txt

    def __lt__(self, other):
        return self.old_term_txt < other.old_term_txt

    def __eq__(self, other):
        return self.old_term_txt == other.old_term_txt

    def __hash__(self):
        return hash(self.old_term_txt)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class Classword:
    cfg_filename_rel = 'un_re/resources/cfg_classwords.lst'
    logical_classword_list = {}
    physical_classword_list = {}

    def __init__(self, logical_classword, physical_classword):
        logical_classword = logical_classword.upper()
        physical_classword = physical_classword.upper()

        self.logical_classword = logical_classword
        self.physical_classword = physical_classword

        Classword.logical_classword_list[logical_classword] = True
        Classword.physical_classword_list[physical_classword] = True

    def __lt__(self, other):
        return self.logical_classword < other.logical_classword

    def __eq__(self, other):
        return self.logical_classword == other.logical_classword

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class ClasswordDatatype:
    cfg_filename_rel = 'un_re/resources/cfg_classword_datatypes.lst'

    def __init__(self, classword, rules_engine_type):
        self.classword = classword
        self.rules_engine_type = rules_engine_type
        self.allowed_datatypes = []

    # A list of ClasswordDatatypeAllowed

    def __lt__(self, other):
        return self.classword < other.classword

    def __eq__(self, other):
        return self.classword == other.classword

    def __hash__(self):
        return hash(self.classword)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class ClasswordDatatypeAllowed:

    def __init__(self, datatype):
        # The initializing datatype might include a size and a
        # byte semantics.   We don't care about the byte semantics, and
        # will disregard that.

        if datatype.find('(') > -1:
            datatype, size = datatype.split('(')
            size = re.sub('BYTE', '', size, re.IGNORECASE)
            size = re.sub('CHAR', '', size, re.IGNORECASE)
            size = size.strip(')')
            self.datatype = datatype.strip()
            self.size = size.strip()
            self.datatype_w_size = f'{self.datatype}({self.size})'
        else:
            self.datatype = datatype.strip()
            self.size = None
            self.datatype_w_size = f'{self.datatype}'

    def __lt__(self, other):
        return self.datatype_w_size < other.datatype_w_size

    def __eq__(self, other):
        return self.datatype_w_size == other.datatype_w_size

    def __hash__(self):
        return hash(self.datatype_w_size)

    def __repr__(self):
        return f"'{self.datatype_w_size}'"


#       def __repr__ (self):
#               line = '\n'+ ('-' * 80) + '\n'
#               line += '{0}\n'.format (
#                       self.__class__.__name__)
#
#               line += '-------------------\n'
#               for k, v in self.__dict__.items ():
#                       line += '{0:20s}: {1}\n'.format (
#                               k,
#                               v)
#               return line

# ===============================================================================
class ClasswordDatatypeVariation:
    cfg_filename_rel = 'un_re/resources/cfg_classword_datatype_variations.lst'

    def __init__(self, classword, column_nm, datatype, size, comment_txt):

        self.classword = classword
        self.column_nm = column_nm
        self.datatype = datatype

        if size == 'None':
            self.size = None
            self.datatype_w_size = self.datatype
        else:
            self.size = size
            self.datatype_w_size = f'{self.datatype}({self.size})'

        self.comment_txt = comment_txt

    def __lt__(self, other):

        if self.classword == other.classword:
            if self.column_nm == other.column_nm:
                if self.datatype == other.datatype:
                    if self.size == other.size:
                        is_lt = False
                    else:
                        is_lt = int(self.size) < int(other.size)
                else:
                    is_lt = self.datatype < other.datatype
            else:
                is_lt = self.column_nm < other.column_nm
        else:
            is_lt = self.classword < other.classword

        # if (is_lt):
        # 	print ('{0}.{1}.{2}.{3} < {4}.{5}.{6}.{7}'.format (
        #		self.classword, self.column_nm, self.datatype, self.size,
        #		other.classword, other.column_nm, other.datatype, other.size))
        return is_lt

    def __eq__(self, other):
        if self.classword == other.classword and \
                self.column_nm == other.column_nm and \
                self.datatype == other.datatype:
            return self.size == other.size
        return False

    def __hash__(self):
        return hash('{0}.{1}.{2}.{3}'.format(
            self.classword,
            self.column_nm,
            self.datatype,
            self.size))

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class ClasswordException:
    cfg_filename_rel = 'un_re/resources/cfg_classword_exceptions.lst'
    physical_classword_exception_list = {}

    def __init__(self, physical_nm, logical_nm):
        self.physical_nm = physical_nm.upper()
        self.logical_nm = logical_nm

        ClasswordException.physical_classword_exception_list[physical_nm] = True

    def __lt__(self, other):
        return self.physical_nm < other.physical_nm

    def __eq__(self, other):
        return self.physical_nm == other.physical_nm

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class Column:
    '''
    The Column object does not have a get_filenum method, because a column
    never stands alone - it is part of a table, which is in a file, and the
    filenum should be retrieved from the parent object.
    '''

    def __init__(self, name_orig, datatype, parent_obj):
        self.position = -1
        self.name_orig = name_orig  # Original physical name

        self.name_upper = name_orig.upper()
        # Uppercased physical name
        if datatype is None:
            # This can happen on COMMENT ON commands
            self.datatype = None
            self.size = None
            self.datatype_w_size = None
        elif datatype.find('(') > -1:
            datatype, size = datatype.split('(')
            size = re.sub('BYTE', '', size, re.IGNORECASE)
            size = re.sub('CHAR', '', size, re.IGNORECASE)
            size = size.strip(')')
            self.size = size.replace(' ', '')

            self.datatype = datatype.strip()
            self.datatype_w_size = f'{self.datatype}({self.size})'
        else:
            self.datatype = datatype.strip()
            self.size = None
            self.datatype_w_size = self.datatype

        self.parent_obj = parent_obj  # Not used, but could be useful.
        self.name_len = len(name_orig)
        self.classword = None  # None until r216 is checked

        self.naming_method: str = ''
        self.column_name_tokens: List[str] = []

        self.title = None

        # Logical attributes
        self.colmn_lgcl_defn_txt = None
        self.colmn_lgcl_nm = None
        # self.colmn_phy_cmmnt_txt	= None # Probably same as comment above
        self.colmn_phy_nm = name_orig
        self.nm_hardend_ind = None
        self.sql_stmt_txt = None
        self.is_identity = False

    def __hash__(self):
        return hash(self.name_upper)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += ('-' * 20) + '\n'
        for k, v in self.__dict__.items():
            line += f'{k:22s}: {v}\n'
        return line


# ===============================================================================
class ColumnComment:
    '''
    For Hive, column comments are created at the same time as the column.
    But for other languages, such as Teradata, they are created separately,
    so they need to be kept in a separate class.
    And Databricks can create column comments either separately or at the
    same time.  Tracking the Column comments separately simplifies the task.

    Column Comments are tracked with a separate class while Table Comments
    aren't, because we check for duplicate column names in the Table
    structure.    Duplicate Table Names can be recognized separately
    but column names belong to a table and can't be recognized separately
    from a table.
    '''

    def __init__(self, database_base_orig, table_name_orig,
                 column_name_orig, comment_txt,
                 input_filename, file_obj_list):

        self.database_base_orig = database_base_orig  # Original physical name
        self.table_name_orig = table_name_orig  # Original physical name
        self.column_name_orig = column_name_orig  # Original physical name
        self.comment_txt = comment_txt
        self.input_filename = input_filename

        self.input_filename_rel = ''
        self.filenum = 0
        self.ruleset = 'ENTERPRISE'
        for file_obj in file_obj_list:
            if file_obj.input_filename == input_filename:
                self.input_filename_rel = file_obj.input_filename_rel
                self.filenum = file_obj.filenum
                self.ruleset = file_obj.ruleset
                break

    @property
    def database_base_upper(self):
        return self.database_base_orig.upper()

    @property
    def table_name_upper(self):
        return self.table_name_orig.upper()

    @property
    def column_name_upper(self):
        return self.column_name_orig.upper()

    def get_input_filename_rel(self):
        return self.input_filename_rel

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += ('-' * 20) + '\n'
        for k, v in self.__dict__.items():
            line += f'{k:22s}: {v}\n'
        return line


# ===============================================================================
class DBXOptimizeStmt:
    def __init__(self, database_base_orig, table_name_orig, zorder_columns,
                 sql_obj, file_obj):
        self.database_base_orig = database_base_orig  # Original physical name
        self.table_name_orig = table_name_orig  # Original physical name
        self.zorder_columns = zorder_columns
        self.sql_obj = sql_obj
        self.file_obj = file_obj

        self.sql_stmt_num = sql_obj.sql_stmt_num

        self.input_filename = file_obj.input_filename
        self.input_filename_rel = file_obj.input_filename_rel
        self.filenum = file_obj.filenum
        self.ruleset = file_obj.ruleset

    @property
    def database_base_upper(self):
        return self.database_base_orig.upper()

    @property
    def table_name_upper(self):
        return self.table_name_orig.upper()

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += ('-' * 20) + '\n'
        for k, v in self.__dict__.items():
            line += f'{k:22s}: {v}\n'
        return line


# ===============================================================================
class ESPStep:
    '''
    Holds attributes of a single step in an ESP job
    '''

    def __init__(self, step_type):
        self.step_type = step_type

        # If the step is a job, it will have a job_name, and possibly
        # additional attributes like an agentname
        self.job_name = ''
        self.agentname = ''
        self.docmember_name = ''
        self.frequency = ''
        self.user = ''
        self.is_external = False
        self.scriptname = ''  # For Linux jobs
        self.cmdname = ''  # For NT jobs
        self.args = ''
        self.resource_agent = ''
        self.resource_buc_code = ''

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# Example Usage
# Create an instance of that class.
# myESPStep = C.ESPStep ('some step type')

# Do something that instance, like set an attribute
# myESP_Step.user = 'Steve Cable'

# Use the __repr__ to specify how to represent this object.
# Represenations are useful for sorting and debugging.
# So I could print the object, and verify that attributes are what they think are set.
# print (myESP_Step)


# ===============================================================================
class ESPJob:
    '''
    Holds attributes about an ESP job, found in wld files.
    Parsed by the ESP_RE rules engine.
    Includes all steps in the ESP job.
    '''

    def __init__(self, input_filename, file_obj_list):

        self.input_filename = input_filename

        self.file_basename = os.path.basename(input_filename)
        self.file_basename = re.sub(r'.wld', '', self.file_basename)

        # That would be the basename of the input filename
        # It would have no path, which would change on
        # deployment.  And no extension, which would be wld.

        self.applid = ''
        self.BUC_code = ''
        self.esp_step = []
        self.invoked_library = ''
        self.num_stmts = 0
        self.found_applstart = False
        self.found_applend = False
        self.top_level_agents = []  # Could be multiple
        self.resource_agents = []  # Could be multiple
        self.resource_buc_code = ''

        self.filenum = 0
        self.input_filename_rel = ''

        for file_obj in file_obj_list:
            if file_obj.input_filename == self.input_filename:
                self.filenum = file_obj.filenum
                self.input_filename_rel = file_obj.input_filename_rel

    def set_applid(self, applid):
        self.applid = applid
        self.BUC_code = applid[:4]

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += 'ESP Job\n'
        line += '-------------------\n'
        line += 'input_filename     : {0}\n'.format(
            self.input_filename)
        line += 'file_basename      : {0}\n'.format(
            self.file_basename)
        line += 'applid             : {0}\n'.format(
            self.applid)
        line += 'BUC_code           : {0}\n'.format(
            self.BUC_code)
        line += 'invoked_library    : {0}\n'.format(
            self.invoked_library)
        line += 'found_applstart    : {0}\n'.format(
            self.found_applstart)
        line += 'found_applend      : {0}\n'.format(
            self.found_applend)
        for i, agent in enumerate(self.top_level_agents):
            line += 'top_level_agent[{0}: {1}\n'.format(
                i,
                agent)
        for i, agent in enumerate(self.resource_agents):
            line += 'resource_agent [{0}] : {1}\n'.format(
                i,
                agent)
        line += 'resource_buc_code  : {0}\n'.format(
            self.resource_buc_code)
        line += 'num_stmts          : {0}\n'.format(
            self.num_stmts)
        line += 'num job steps      : {0}\n'.format(
            len(self.esp_step))
        for i, step in enumerate(self.esp_step):
            if step.step_type in ('JOB', 'LINUX_JOB', 'AIX_JOB', 'NT_JOB'):
                line += 'esp_step[{0}]'.format(i)
                line += '  {0} {1}\n'.format(
                    step.step_type,
                    step.job_name)
                line += '  AGENT {0}\n'.format(
                    step.agentname)
        return line

    def get_filenum(self, file_obj_list):
        for file_obj in file_obj_list:
            if file_obj.input_filename == self.input_filename:
                return file_obj.filenum
        return -1

    def get_input_filename_rel(self):
        return self.input_filename_rel


# ===============================================================================
class External_Name(Abbreviation):
    cfg_filename_rel = 'un_re/resources/cfg_extrnl_nm.lst'


# ===============================================================================
class InputFile:
    def __init__(self, input_filename, input_filename_rel, filenum):
        self.input_filename = input_filename
        # The full filename, including the path
        self.input_filename_rel = input_filename_rel
        self.filenum = filenum

        self.ruleset = 'ENTERPRISE'
        self.user_story_id = ''
        self.num_findings = 0
        # At the end, we will post a success record for files
        # with no findings

        self.is_utf8_readable = True  # Suppose True to start with.

        self.has_a_syntax_error = False  # Suppose False to start with.
        self.contents = None
        self.num_statements = 0  # Num SQL statements
        self.num_lines = 0  # Num lines in the whole file.

        self.command_counter = {}

    # def get_filenum (self):
    #	return self.filenum

    # def get_input_filename (self):
    #	return self.input_filename

    def get_input_filename_rel(self):
        return self.input_filename_rel

    # If you want to print an object, the repr object will let you say
    # print (G.FILE_OBJ) for example
    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += 'Input File          \n'
        line += '--------------------\n'
        line += 'Input Filename          : {0}\n'.format(
            self.input_filename)
        line += 'Input Filename Rel      : {0}\n'.format(
            self.input_filename_rel)
        line += 'FileNum                 : {0}\n'.format(
            self.filenum)
        line += 'Ruleset                 : {0}\n'.format(
            self.ruleset)
        line += 'User Story ID           : {0}\n'.format(
            self.user_story_id)
        line += 'Num Findings            : {0}\n'.format(
            self.num_findings)
        line += 'has_a_syntax_error      : {0}\n'.format(
            self.has_a_syntax_error)
        line += 'is_utf8_readable        : {0}\n'.format(
            self.is_utf8_readable)
        return line


# def __lt__ (self, other):
# 	return (self.input_filename < other.input_filename)

# def __eq__(self, other):
# 	return self.input_filename==other.input_filename

# def __hash__(self):
# 	return hash (self.input_filename)


# ===============================================================================
class MultisetBaseTable:
    cfg_filename_rel = 'un_re/resources/cfg_multiset_base_tables.lst'

    def __init__(self, table_nm, comment_txt):
        self.table_nm = table_nm
        self.comment_txt = comment_txt

    def __lt__(self, other):
        return self.table_nm < other.table_nm

    def __eq__(self, other):
        return self.table_nm == other.table_nm

    def __hash__(self):
        return hash(self.table_nm)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class RulesException:
    cfg_filename_rel = 'un_re/resources/cfg_rules_exceptions.lst'

    def __init__(self, rule_id, project_nm, table_nm, column_nm, exp_yyyymmdd_dt, comment_txt):
        self.rule_id = rule_id
        self.project_nm = project_nm
        self.table_nm = table_nm
        self.column_nm = column_nm
        self.exp_yyyymmdd_dt = exp_yyyymmdd_dt
        self.comment_txt = comment_txt
        self.is_expired = False

        self.pk = f'{rule_id}|{project_nm}|{table_nm}|{column_nm}'

    def __lt__(self, other):
        return self.pk < other.pk

    def __eq__(self, other):
        return self.pk == other.pk

    # It is probably unnecessary to specify this operator, because
    # we scan the table linearly to match the ALL wildcard

    def __hash__(self):
        return hash(self.pk)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class SQLStatementObj:
    '''
    This class will hold all SQL statements.
    These statements maybe further classified into other, additional
    classes by other functions.
    '''

    def __init__(self, sql_stmt_num, sql_stmt_txt, command_type,
                 input_filename, input_filename_rel, antlr_log_filename,
                 file_obj):

        self.sql_stmt_num = sql_stmt_num
        # That would the number of the
        # sql statement WITHIN that input_filename

        self.sql_stmt_txt = sql_stmt_txt
        self.command_type = command_type
        # For example INSERT, UPDATE, DELETE

        self.input_filename = input_filename
        self.input_filename_rel = input_filename_rel

        self.filenum = 0
        self.ruleset = 'ENTERPRISE'

        self.input_file = file_obj
        self.ruleset = file_obj.ruleset
        self.filenum = file_obj.filenum

        # Adding the input_file object make some other attributes
        # redundant, but will keep them now for backwards
        # compatibility.  Remove them when ready.

        self.antlr_log_filename = antlr_log_filename
        # That filename will hold the results of
        # parsing with Antlr.

        self.antlr_log_contents = None
        # This will be set after initialization

        self.antlr_status = None

        self.local_script_name = None
        self.tentative_command_type = 'UNKNOWN'
        self.temp_sql_filename = None  # Where the SQL statement is written.

    def get_filenum(self, file_obj_list):
        for file_obj in file_obj_list:
            if file_obj.input_filename == self.input_filename:
                return file_obj.filenum
        return None

    def get_input_filename_rel(self):
        return self.input_filename_rel

    def get_a_little_context(self):
        '''
        Return the first 3 wrapped lines of the SQL statement.
        This provides a little context without reprint the whole statement.
        '''

        line_num = 0
        preview_lines = []
        for line in self.sql_stmt_txt.split('\n'):
            line_fragment = '\n'.join(textwrap.wrap(line, width=80, replace_whitespace=False))
            for line_segment in line_fragment.split('\n'):
                preview_lines.append(line_segment)
                line_num += 1
            if line_num == 3:
                break
        return preview_lines

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class OtherStatement:
    '''
    This class will hold other, non-Create Table and non-Create View
    statements, like DML statements.

    Tables and Views are stored in the classes below this class.
    '''

    def __init__(self, sql_stmt_num, sql_stmt_txt, command_type,
                 input_filename, input_filename_rel, file_obj_list):

        self.sql_stmt_num = sql_stmt_num
        self.sql_stmt_txt = sql_stmt_txt
        self.command_type = command_type
        # For example INSERT, UPDATE, DELETE

        self.input_filename = input_filename
        self.input_filename_rel = input_filename_rel

        self.filenum = 0
        self.ruleset = 'ENTERPRISE'  # Default
        for file_obj in file_obj_list:
            if file_obj.input_filename == input_filename:
                self.filenum = file_obj.filenum
                self.ruleset = file_obj.ruleset
                break

        self.file_obj = None  # See that after initialization.

    # Granted that seems redundant, and is added for compatibility
    # with the Oracle Rules, which demonstrated the benefit.
    # The old  redundant attributes can be removed when ready.

    def get_filenum(self, file_obj_list):
        for file_obj in file_obj_list:
            if file_obj.input_filename == self.input_filename:
                return file_obj.filenum
        return -1

    # def get_input_filename_rel (self):
    # 	self.input_filename_rel

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += 'Other Statement\n'
        line += '-------------------\n'
        line += 'SQL Stmt Num      : {0}\n'.format(
            self.sql_stmt_num + 1)
        line += 'SQL Statement     : {0}\n'.format(
            self.sql_stmt_txt)
        line += 'Command Type      : {0}\n'.format(
            self.command_type)
        line += 'Input Filename Rel: {0}\n'.format(
            self.input_filename_rel)
        line += 'Ruleset           : {0}\n'.format(
            self.ruleset)
        return line


# ===============================================================================
class TableStructure(Table_Extrt):

    def __init__(self, database_base_orig, table_name_orig, sql_stmt_obj):

        super().__init__(
            model_id='UNKNOWN',
            model_nm='UNKNOWN',
            entty_defn_txt='UNKNOWN',
            entty_id='UNKNOWN',
            entty_nm='UNKNONW')

        self.sql_stmt_num = sql_stmt_obj.sql_stmt_num
        self.sql_stmt_txt = sql_stmt_obj.sql_stmt_txt
        self.command_type = sql_stmt_obj.command_type
        self.antlr_log_filename = sql_stmt_obj.antlr_log_filename

        self.database_base_orig = database_base_orig

        self.table_name_orig = table_name_orig
        self.sql_stmt_obj = sql_stmt_obj

        self.input_filename = sql_stmt_obj.input_file.input_filename
        self.input_filename_rel = sql_stmt_obj.input_file.input_filename_rel
        self.filenum = sql_stmt_obj.input_file.filenum
        self.ruleset = sql_stmt_obj.input_file.ruleset

        self.naming_method: str = ''
        self.table_name_tokens: List[str] = []

        self.regulated_options = []
        # The only regulated option is NO PRIMARY INDEX

        self.column_elements = []

        self.num_collect_stats = 0
        # self.num_ct_commands		= 0 	# Num Create Table commands, used by r260

        self.foreign_key_clauses = []
        self.primary_key_is_specified = False

        # self.redshift_distkey	= False, or ''
        # Create a child class to hold vendor-specific attributes.

        self.tablespaces = []

    # A partitioned table could be spread across
    # multiple tablespaces

    @property
    def database_base_upper(self):
        # This property will let me reference Table_Struct.database_name_upper
        return self.database_base_orig.upper()

    @property
    def table_name_upper(self):
        return self.table_name_orig.upper()

    def get_column_element(self, column_name_upper):
        for column_element in self.column_elements:
            if column_element.column_name_upper == column_name_upper:
                return column_element
        return None

    def get_filenum(self, file_obj_list):
        for file_obj in file_obj_list:
            if file_obj.input_filename == self.input_filename:
                return file_obj.filenum
        return None

    def get_input_filename_rel(self):
        return self.input_filename_rel

    # def add_column_element (self, Column):
    #	self.column_elements.append (Column)

    # def set_database_base (self, database_base_orig):
    #	self.database_base_orig  = database_base_orig
    #	self.database_base_upper = database_base_orig.upper ()

    def increment_num_collect_stats(self):
        self.num_collect_stats += 1

    def __hash__(self):
        return hash(self.database_base_upper + '.' + self.table_name_upper)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += 'Table Structure\n'
        line += '----------------------------\n'
        line += 'SQL Stmt Num               : {0}\n'.format(
            self.sql_stmt_num)
        line += 'Database Base              : {0}\n'.format(
            self.database_base_orig)
        line += 'Table Name                 : {0}\n'.format(
            self.table_name_orig)
        line += 'Table Name Upper           : {0}\n'.format(
            self.table_name_upper)
        line += 'Tbl Nm Tokens              : {0}\n'.format(
            self.table_name_tokens)
        line += 'Naming Method              : {0}\n'.format(
            self.naming_method)
        line += 'Command type               : {0}\n'.format(
            self.command_type)
        line += 'Num Collect Stats Cmds     : {0}\n'.format(
            self.num_collect_stats)
        line += 'Primary Key Is Specified   : {0}\n'.format(
            self.primary_key_is_specified)

        num_elements = len(self.column_elements)
        line += 'Num Column Elements        : {0}\n'.format(num_elements)
        for i in range(num_elements):
            line += '    Column                        : {0}\n'.format(i)
            line += '    Column name                   : {0}\n'.format(self.column_elements[i].name_orig)
            line += '    Column datatype               : {0}\n'.format(self.column_elements[i].datatype)
            line += '    Column datatype_w_size        : {0}\n'.format(self.column_elements[i].datatype_w_size)
            line += '    Column is_identity            : {0}\n'.format(self.column_elements[i].is_identity)

        if self.regulated_options is None:
            line += 'Regulated Options  : None\n'
        else:
            for option in self.regulated_options:
                line += 'Regulated Option   : {0}\n'.format(
                    option)
        line += 'Input Filename             : {0}\n'.format(
            self.input_filename)
        line += 'SQL Statement Obj          : {0}\n'.format(
            self.sql_stmt_obj)
        return line


# ===============================================================================
class TableComment:
    '''
    Table comments are tracked separately from the Table Structure because
    the Table Structure could be initialized for either a Create Table
    comment or an Alter Table command.    The Create Table command should
    have an accompanying Comment On Table command, but the Alter Table
    command does not need to.

    Tracking the Column comments separately simplifies the task.
    '''

    def __init__(self, database_base_orig, table_name_orig,
                 comment_txt,
                 sql_statement_obj):
        self.database_base_orig = database_base_orig  # Original physical name
        self.table_name_orig = table_name_orig  # Original physical name
        self.comment_txt = comment_txt
        self.sql_statement_obj = sql_statement_obj

    @property
    def sql_stmt_num(self):
        return self.sql_statement_obj.sql_stmt_num

    @property
    def filenum(self):
        return self.sql_statement_obj.filenum

    @property
    def input_filename_rel(self):
        return self.sql_statement_obj.input_filename_rel

    @property
    def input_filename(self):
        return self.sql_statement_obj.input_filename

    @property
    def database_base_upper(self):
        return self.database_base_orig.upper()

    @property
    def table_name_upper(self):
        return self.table_name_orig.upper()

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += ('-' * 20) + '\n'
        for k, v in self.__dict__.items():
            line += f'{k:22s}: {v}\n'
        return line


# ===============================================================================
class HiveTableStructure(TableStructure):
    def __init__(self, database_base_orig, table_name_orig,
                 # generic attributes are inherited from the base Table Structure.

                 sql_stmt_obj):
        TableStructure.__init__(self, database_base_orig, table_name_orig,
                                sql_stmt_obj)

        self.hive_storage_type = ''

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += 'Hive Table Structure\n'
        line += '------------------------\n'
        line += 'SQL Stmt Num     : {0}\n'.format(
            self.sql_stmt_num + 1)
        line += 'Database Base    : {0}\n'.format(
            self.database_base_orig)
        line += 'Table Name       : {0}\n'.format(
            self.table_name_orig)
        line += 'Tbl Nm Tokens    : {0}\n'.format(
            self.table_name_tokens)
        line += 'Command type     : {0}\n'.format(
            self.command_type)
        line += 'Hive Storage Type: {0}\n'.format(
            self.hive_storage_type)
        return line


# ===============================================================================
class RedshiftTableStructure(TableStructure):
    def __init__(self, database_base_orig, table_name_orig,
                 # generic attributes are inherited from the base Table Structure.

                 sql_stmt_obj):
        TableStructure.__init__(self, database_base_orig, table_name_orig,
                                sql_stmt_obj)

        self.distkey = False
        self.distkey_column = None

    def set_distkey(self, found_distkey, column_name):
        self.distkey = found_distkey
        self.distkey_column = column_name

    # add other redshift-specific attributes here

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += 'Redshift Table Structure\n'
        line += '------------------------\n'
        line += 'SQL Stmt Num  : {0}\n'.format(
            self.sql_stmt_num + 1)
        line += 'Database Base : {0}\n'.format(
            self.database_base_orig)
        line += 'Table Name    : {0}\n'.format(
            self.table_name_orig)
        line += 'Tbl Nm Tokens : {0}\n'.format(
            self.table_name_tokens)
        line += 'Command type  : {0}\n'.format(
            self.command_type)
        line += 'Distkey       : {0}\n'.format(
            self.distkey)
        line += 'Distkey Column: {0}\n'.format(
            self.distkey_column)
        return line


# ===============================================================================
class GrantStatementObj(SQLStatementObj):
    '''
    A GRANT statement is a certain kind of SQL Statement
    '''

    def __init__(self, sql_stmt_obj):
        SQLStatementObj.__init__(self,
                                 sql_stmt_num=sql_stmt_obj.sql_stmt_num,
                                 sql_stmt_txt=sql_stmt_obj.sql_stmt_txt,
                                 command_type=sql_stmt_obj.command_type,
                                 input_filename=sql_stmt_obj.input_file.input_filename,
                                 input_filename_rel=sql_stmt_obj.input_file.input_filename_rel,
                                 antlr_log_filename=sql_stmt_obj.antlr_log_filename,
                                 file_obj=sql_stmt_obj.input_file)

        self.temp_sql_filename = sql_stmt_obj.temp_sql_filename

        self.command_type = sql_stmt_obj.command_type

        self.antlr_log_filename = sql_stmt_obj.antlr_log_filename
        self.antlr_log_contents = sql_stmt_obj.antlr_log_contents

        self.granted_permission = None
        self.grantee = None

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += '{0}\n'.format(
            self.__class__.__name__)

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += '{0:20s}: {1}\n'.format(
                k,
                v)
        return line


# ===============================================================================
class Index_Obj:

    def __init__(self,
                 database_base_orig,
                 index_name_orig,
                 sql_stmt_obj
                 ):
        self.database_base_orig = database_base_orig
        self.index_name_orig = index_name_orig

        self.tablespaces = []

        self.sql_stmt_obj = sql_stmt_obj

        self.ruleset = 'ENTERPRISE'
        # Setup a TechDebt ruleset someday if it is called for.

        self.input_filename = sql_stmt_obj.input_file.input_filename
        self.input_filename_rel = sql_stmt_obj.input_file.input_filename_rel

    @property
    def filename_rel(self):
        return self.sql_stmt_obj.input_file.filename_rel

    @property
    def filenum(self):
        return self.sql_stmt_obj.input_file.filenum

    @property
    def database_base_upper(self):
        # This property will let me reference Table_Struct.database_name_upper
        return self.database_base_orig.upper()

    @property
    def index_name_upper(self):
        return self.index_name_orig.upper()

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += '{0}\n'.format(
            self.__class__.__name__)

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += '{0:20s}: {1}\n'.format(
                k,
                v)
        return line


# ===============================================================================
class ViewStructure:
    def __init__(self, database_base_orig, view_name_orig,
                 sql_stmt_obj):

        self.database_base_orig = database_base_orig
        self.database_base_upper = database_base_orig.upper()

        self.view_name_orig = view_name_orig

        self.input_filename = sql_stmt_obj.input_file.input_filename
        self.input_filename_rel = sql_stmt_obj.input_file.input_filename_rel

        self.ruleset = sql_stmt_obj.input_file.ruleset
        self.filenum = sql_stmt_obj.input_file.filenum

        self.sql_stmt_num = sql_stmt_obj.sql_stmt_num
        self.sql_stmt_txt = sql_stmt_obj.sql_stmt_txt
        self.command_type = sql_stmt_obj.command_type

    # For example CREATE VIEW

    @property
    def view_name_upper(self):
        return self.view_name_orig.upper()

    def get_filenum(self, file_obj_list):
        for file_obj in file_obj_list:
            if file_obj.input_filename == self.input_filename:
                return file_obj.filenum
        return None

    def get_input_filename_rel(self):
        return self.input_filename_rel

    def __hash__(self):
        return hash(self.database_base_upper + '.' + self.view_name_upper)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += 'View Structure\n'
        line += '---------------\n'
        line += 'database_base_upper: {0}\n'.format(
            self.database_base_upper)
        line += 'view_name_upper    : {0}\n'.format(
            self.view_name_upper)
        line += 'command_type       : {0}\n'.format(
            self.command_type)
        line += 'input_filename_rel : {0}\n'.format(
            self.input_filename_rel)
        line += 'ruleset            : {0}\n'.format(
            self.ruleset)
        line += 'sql_stmt_txt       : {0}\n'.format(
            self.sql_stmt_txt)
        return line


# ===============================================================================
class Rule:
    rules_urls_filename = '/un_re/resources/rules_urls.lst'

    def __init__(self, rule_id, severity):
        self.rule_id = rule_id
        self.severity = severity
        self.url = None

    def __hash__(self):
        return hash(self.rule_id)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line


# ===============================================================================
class TechdebtExclusion:
    cfg_filename_rel = 'un_re/resources/cfg_techdebt_exclusions.lst'

    def __init__(self, object_nm, activation_yyyymmdd_dt, is_active):
        self.object_nm = object_nm
        self.activation_yyyymmdd_dt = activation_yyyymmdd_dt
        self.is_active = is_active

    def __lt__(self, other):
        return self.object_nm < other.object_nm and self.is_active

    def __eq__(self, other):
        return (self.object_nm == other.object_nm) and self.is_active

    def __hash__(self):
        return hash(self.object_nm)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:23s}: {v}\n'
        return line


# ===============================================================================
class UnclearedTechdebt:
    def __init__(self, days_ago, input_file_nm):
        self.days_ago = int(days_ago)
        self.input_file_nm = input_file_nm

    def __lt__(self, other):
        return self.input_file_nm < other.input_file_nm

    def __eq__(self, other):
        return self.input_file_nm == other.input_file_nm

    def __hash__(self):
        return hash(self.input_file_nm)

    def __repr__(self):
        line = '\n' + ('-' * 80) + '\n'
        line += f'{self.__class__.__name__}\n'

        line += '-------------------\n'
        for k, v in self.__dict__.items():
            line += f'{k:20s}: {v}\n'
        return line
