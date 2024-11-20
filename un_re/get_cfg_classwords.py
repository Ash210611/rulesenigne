# pylint: disable=C0209			# Don't require formatted strings.

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
def get_classword_DMV_rows():
    '''
    Retrieve the rows from the database.
    '''

    sql = 'select clss_word_lgcl_nm, clss_word_phy_nm ' + \
          'from dmv.valdtn_ref_clss_word;'

    rows = run_pg_statement(sql)

    return rows


# ===============================================================================
def get_classwords_DMV():
    '''
    This function will download the cfg records
    from the DMV Postgres database
    '''

    rows = get_classword_DMV_rows()

    for row in rows:
        (logical_classword, physical_classword) = (row[0], row[1])

        logical_classword = logical_classword.strip()
        physical_classword = physical_classword.strip()

        classword_obj = C.Classword(logical_classword, physical_classword)

        G.CLASSWORD_LIST.append(classword_obj)

    if G.VERBOSE:
        num = len(G.CLASSWORD_LIST)
        if num == 1:
            indent('Read {0:5,d} classword from the DMV database.'.format(num))
        else:
            indent('Read {0:5,d} classwords from the DMV database.'.format(num))


# ===============================================================================
def save_classwords_locally():
    '''
    Save database rows to a local file for disaster recovery.
    '''

    logical_classword_len = len('logical_classword')
    physical_classword_len = len('physical_classword')

    for rec in G.CLASSWORD_LIST:
        logical_classword_len = max(logical_classword_len, len(rec.logical_classword))
        physical_classword_len = max(physical_classword_len, len(rec.physical_classword))

    rec_format = '{{0:{0}s}} | {{1:{1}s}} '.format(
        logical_classword_len + 2,  # + 2 for the comment symbol
        physical_classword_len
    )

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.Classword.cfg_filename_rel)

    with open(cfg_filename, 'w', encoding='utf-8') as cfg_file:

        fprint(cfg_file, '# Filename: {0}'.format(
            cfg_filename.replace(G.SCRIPT_DIR, '$SCRIPT_DIR')))
        fprint(cfg_file, '#')

        rows = get_cfg_table_comment('dmv', 'valdtn_ref_clss_word')

        for row in rows:
            for line in row[0].split('\n'):
                fprint(cfg_file, f'# {line}')
        fprint(cfg_file, '#')

        fprint(cfg_file, rec_format.format(
            '# ' + 'logical_classword',
            'physical_classword'
        ))

        fprint(cfg_file, rec_format.format(
            '# ' + '-' * logical_classword_len,
            '-' * physical_classword_len
        ))

        for rec in sorted(G.CLASSWORD_LIST):
            fprint(cfg_file, rec_format.format(
                rec.logical_classword,
                rec.physical_classword
            ))


# ===============================================================================
def get_classwords_locally():
    '''
    Read from a local file.
    '''

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.Classword.cfg_filename_rel)

    with open(cfg_filename, 'r', encoding='utf-8') as cfg_file:
        for line in cfg_file.readlines():
            if line.find('#') > -1:
                continue

            line = line.strip()
            logical_classword = line.split('|')[0]
            physical_classword = line.split('|')[1]

            logical_classword = logical_classword.strip()
            physical_classword = physical_classword.strip()

            classword_obj = C.Classword(logical_classword, physical_classword)

            G.CLASSWORD_LIST.append(classword_obj)

    if G.VERBOSE:
        num = len(G.CLASSWORD_LIST)
        if G.GET_CFG_FROM_GIT:
            source = 'from Git'
        else:
            source = 'locally'

        if num == 1:
            indent(f'Read 1 classword {source}.')
        else:
            indent(f'Read {num:5,d} classwords {source}.')


# ===============================================================================
def add_missing_classwords():
    # The database has Identifier/ID
    # Add Id/ID not in the database, so add that manually
    logical_classword = 'Id'
    physical_classword = 'ID'

    classword_obj = C.Classword(logical_classword, physical_classword)

    G.CLASSWORD_LIST.append(classword_obj)


# ===============================================================================
def get_classwords_GIT():
    '''
    Read the latest cfg records from the Git repo.
    '''

    log_filename = '{0}/{1}.log'.format(
        G.TEMP_DIR,
        os.path.splitext(os.path.basename(__file__))[0])

    os_command = 'wget {0} -O {1} >{2} 2>&1'.format(
        f'{G.GIT_URL}/{C.Classword.cfg_filename_rel}',
        f'{G.SCRIPT_DIR}/{C.Classword.cfg_filename_rel}',
        log_filename)

    try:
        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error(f'Child was terminated by signal {-ret}')
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

        get_classwords_locally()

    except OSError as e:
        G.LOGGER.error(f'Git-archive execution failed: {e}')
        indent(f'Failed: {os_command}')


# ===============================================================================
def get_cfg_classwords():
    '''
    First try to read the list of classwords dynamically from the
    Data-Modeler's Postres database.

    Actually there are two lists, because they sort into different orders,
    and are used in different contexts.   The Physical list is used when
    snake case is used.  The Logical list is used when snake case is not
    used.

    If the DM database is down, there is a file backup we can read from..
    Try to read the cfg records from the DMV first.
    If that succeeds, save them locally for the next release.
    Or if that fails, use the local copy to read from.
    '''

    if G.RULES_ENGINE_TYPE == 'ESP_RE':
        # These things are not needed for this rules engine
        return

    if 'r216' not in G.SHOULD_CHECK_RULE and \
            'r004' not in G.SHOULD_CHECK_RULE:
        return

    if G.GET_CFG_FROM_GIT:
        get_classwords_GIT()
    else:
        get_classwords_DMV()

        if len(G.CLASSWORD_LIST) > 0:

            save_classwords_locally()

        else:
            get_classwords_locally()

    add_missing_classwords()

    G.LOGICAL_CLASSWORD_LIST = sorted(C.Classword.logical_classword_list)
    G.PHYSICAL_CLASSWORD_LIST = sorted(C.Classword.physical_classword_list)
