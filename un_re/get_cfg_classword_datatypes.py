# pylint: disable=C0209			# Dont' require formatted strings.
# pylint: disable=C0206			# Cannot iterate over items ()
# pylint: disable=C0201			# Don't want to iterate over keys ()

import os
import subprocess
import sys

import un_re.ERROR_NUMBERS as E
import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.fprint import fprint
from un_re.get_cfg_table_comment import get_cfg_table_comment
from un_re.indent import indent
from un_re.run_pg_statement import run_pg_statement


# ===============================================================================
def get_classword_datatype_DB_rows():
    '''
    Retrieve the rows from the database.
    '''

    sql = "select classword_typ, rules_engine_typ, datatypes_txt " + \
          "from rulesengine.cfg_classword_datatype " + \
          "order by classword_typ, " + \
          "    case rules_engine_typ " + \
          "        when 'ANY' then 1 " + \
          "        when 'OTHER' then 99 " + \
          "        else 2 " + \
          "        END " + \
          ";"

    rows = run_pg_statement(sql)

    return rows


# ======== =======================================================================
def get_classword_datatypes_DB():
    '''
    This function will download the classword_datatypes from the
    Postgres database
    '''

    rows = get_classword_datatype_DB_rows()

    for row in rows:
        classword_id = row[0]
        rules_engine_typ = row[1]
        datatypes_txt = row[2]

        add_classword_datatype(classword_id, rules_engine_typ, datatypes_txt)

    if len(rows) > 0:
        save_classword_datatypes_locally(rows)

    if G.VERBOSE:
        num = len(G.CLASSWORD_DATATYPES)
        if num == 1:
            indent('Read 1 classword-datatype list from the DMV database.')
        else:
            indent(f'Read {num:5,d} classword-datatype lists from the DMV database.')


# ===============================================================================
def add_classword_datatype(classword, this_rules_engine_type, comma_delimited_datatypes):
    classword = classword.strip()
    this_rules_engine_type = this_rules_engine_type.strip()
    comma_delimited_datatypes = comma_delimited_datatypes.strip()

    classword_datatype_obj = C.ClasswordDatatype(classword, this_rules_engine_type)

    for datatype in comma_delimited_datatypes.split(','):
        allowed_datatype = C.ClasswordDatatypeAllowed(datatype)

        classword_datatype_obj.allowed_datatypes.append(allowed_datatype)

    if classword not in G.CLASSWORD_DATATYPES.keys():
        # Add it.

        # If the datatypes for this classword have not
        # been appended yet, then add them.  Give
        # priority to the specific rules engine first.

        # Do not read the logic below to say that we will append
        # no matter what kind of Rules Engine Type is specified.
        # The elifs are exclusive, so understand that they
        # should be read in that order.

        if this_rules_engine_type == 'ANY':
            G.CLASSWORD_DATATYPES[classword] = classword_datatype_obj
        elif this_rules_engine_type == G.RULES_ENGINE_TYPE:
            G.CLASSWORD_DATATYPES[classword] = classword_datatype_obj
        elif this_rules_engine_type == 'OTHER':
            G.CLASSWORD_DATATYPES[classword] = classword_datatype_obj


# ===============================================================================
def get_classword_datatypes_locally():
    cfg_filename = os.path.join(G.SCRIPT_DIR, C.ClasswordDatatype.cfg_filename_rel)

    G.CLASSWORD_DATATYPES = {}

    with open(cfg_filename, 'r', encoding='utf-8') as cfg_file:
        for line in cfg_file.readlines():
            if line.find('#') > -1:
                continue

            line = line.strip()
            classword, this_rules_engine_type, comma_delimited_datatypes = line.split('|')

            add_classword_datatype(classword, this_rules_engine_type, comma_delimited_datatypes)

    if G.VERBOSE:
        num = len(G.CLASSWORD_DATATYPES)
        if G.GET_CFG_FROM_GIT:
            source = 'from Git'
        else:
            source = 'locally'

        if num == 1:
            indent(f'Read 1 classword-datatype list {source}.')
        else:
            indent(f'Read {num:5,d} classword-datatype lists {source}.')


# ===============================================================================
def save_classword_datatypes_locally(rows):
    '''
    Save database rows to a local file for disaster recovery.
    '''

    classword_id_len = len('classword_id')
    rules_engine_typ_len = len('rules_engine_type')
    datatypes_txt_len = len('datatypes_txt')

    for row in rows:
        classword = row[0].strip()
        rules_engine_type = row[1].strip()
        datatypes_txt = row[2].strip()

        classword_id_len = max(classword_id_len, len(classword))
        rules_engine_typ_len = max(rules_engine_typ_len, len(rules_engine_type))
        datatypes_txt_len = max(datatypes_txt_len, len(datatypes_txt))

    rec_format = '{{0:{0}s}} | {{1:{1}s}} | {{2:{2}s}}'.format(
        classword_id_len + 2,  # + 2 for the comment symbol
        rules_engine_typ_len,
        datatypes_txt_len)

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.ClasswordDatatype.cfg_filename_rel)

    with open(cfg_filename, 'w', encoding='utf-8') as cfg_file:

        fprint(cfg_file, '# Filename: {0}'.format(
            cfg_filename.replace(G.SCRIPT_DIR, '$SCRIPT_DIR')))
        fprint(cfg_file, '#')

        table_comments = get_cfg_table_comment('rulesengine', 'cfg_classword_datatype')

        for row in table_comments:
            for line in row[0].split('\n'):
                fprint(cfg_file, f'# {line}')
        fprint(cfg_file, '#')

        fprint(cfg_file, rec_format.format(
            '# ' + 'classword_id',
            'rules_engine_typ',
            'datatypes_txt'))

        fprint(cfg_file, rec_format.format(
            '# ' + '-' * classword_id_len,
            '-' * rules_engine_typ_len,
            '-' * datatypes_txt_len))

        for row in rows:
            classword = row[0].strip()
            rules_engine_type = row[1].strip()
            datatypes_txt = row[2].strip()

            fprint(cfg_file, rec_format.format(
                classword,
                rules_engine_type,
                datatypes_txt))


# ===============================================================================
def get_classword_datatypes_GIT():
    '''
    Read the latest cfg records from the Git repo.
    '''

    log_filename = '{0}/{1}.log'.format(
        G.TEMP_DIR,
        os.path.splitext(os.path.basename(__file__))[0])

    os_command = 'wget {0} -O {1} >{2} 2>&1'.format(
        f'{G.GIT_URL}/{C.ArrayException.cfg_filename_rel}',
        f'{G.SCRIPT_DIR}/{C.ArrayException.cfg_filename_rel}',
        log_filename)

    try:
        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error(f'Child was terminated by signal {-ret}')
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

        get_classword_datatypes_locally()

    except OSError as e:
        G.LOGGER.error(f'Git-archive execution failed: {e}')
        indent(f'Failed: {os_command}')


# ======== =======================================================================
def get_cfg_classword_datatypes():
    if G.RULES_ENGINE_TYPE == 'ESP_RE':
        # These things are not needed for this rules engine
        return

    # -----------------------------------------------------------------------
    # Only load this list if there are rules that will use it.
    rules_that_need_classword_datatypes = ['r306', 'r424', 'r004']
    # Technically there are more

    intersection = list(set(rules_that_need_classword_datatypes) &
                        set(G.SHOULD_CHECK_RULE))
    if len(intersection) == 0:
        return

    # -----------------------------------------------------------------------
    if G.GET_CFG_FROM_GIT:
        get_classword_datatypes_GIT()
    else:
        get_classword_datatypes_DB()

        if len(G.CLASSWORD_DATATYPES) > 0:

            pass
        # Most cfg tables are saved locally here, but classwords
        # are filtered, so they are saved differently

        else:
            get_classword_datatypes_locally()
