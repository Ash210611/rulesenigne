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
def get_classword_exception_DMV_rows():
    '''
    Retrieve the rows from the database.
    '''

    sql = 'select clss_word_excep_phy_nm, ' + \
          ' clss_word_excep_lgcl_nm ' + \
          'from dmv.valdtn_ref_clss_word_excep;'

    rows = run_pg_statement(sql)

    return rows


# ===============================================================================
def get_classword_exceptions_DMV():
    '''
    This function will download the cfg records
    from the DMV Postgres database
    '''

    rows = get_classword_exception_DMV_rows()

    for row in rows:
        (physical_nm, logical_nm) = (row[0], row[1])

        physical_nm = physical_nm.strip()
        logical_nm = logical_nm.strip()

        exc_obj = C.ClasswordException(physical_nm,
                                       logical_nm)

        G.CLASSWORD_EXCEPTIONS.append(exc_obj)

    G.PHYSICAL_CLASSWORD_EXCEPTION_LIST = list(
        sorted(C.ClasswordException.physical_classword_exception_list.keys()))

    if G.VERBOSE:
        num = len(G.CLASSWORD_EXCEPTIONS)
        if num == 1:
            indent('Read 1 classword exception from the DMV database.')
        else:
            indent('Read {0:5,d} classword exceptions from the DMV database.'.format(num))


# ===============================================================================
def save_classword_exceptions_locally():
    '''
    Save database rows to a local file for disaster recovery.
    '''

    physical_nm_len = len('physical_nm')
    logical_nm_len = len('logical_nm')

    for rec in G.CLASSWORD_EXCEPTIONS:
        physical_nm_len = max(physical_nm_len, len(rec.physical_nm))
        logical_nm_len = max(logical_nm_len, len(rec.logical_nm))

    rec_format = '{{0:{0}s}} | {{1:{1}s}} '.format(
        physical_nm_len + 2,  # + 2 for the comment symbol
        logical_nm_len
    )

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.ClasswordException.cfg_filename_rel)

    with open(cfg_filename, 'w', encoding='utf-8') as cfg_file:

        fprint(cfg_file, '# Filename: {0}'.format(
            cfg_filename.replace(G.SCRIPT_DIR, '$SCRIPT_DIR')))
        fprint(cfg_file, '#')

        rows = get_cfg_table_comment('dmv', 'valdtn_ref_clss_word_excep')

        for row in rows:
            for line in row[0].split('\n'):
                fprint(cfg_file, f'# {line}')
        fprint(cfg_file, '#')

        fprint(cfg_file, rec_format.format(
            '# ' + 'physical_nm',
            'logical_nm'
        ))

        fprint(cfg_file, rec_format.format(
            '# ' + '-' * physical_nm_len,
            '-' * logical_nm_len
        ))

        for rec in sorted(G.CLASSWORD_EXCEPTIONS):
            fprint(cfg_file, rec_format.format(
                rec.physical_nm,
                rec.logical_nm
            ))


# ===============================================================================
def get_classword_exceptions_locally():
    cfg_filename = os.path.join(G.SCRIPT_DIR, C.ClasswordException.cfg_filename_rel)

    with open(cfg_filename, 'r', encoding='utf-8') as cfg_file:
        for line in cfg_file.readlines():
            if line.find(r'#') > -1:
                continue

            physical_nm = line.split('|')[0]
            logical_nm = line.split('|')[1]

            physical_nm = physical_nm.strip()
            logical_nm = logical_nm.strip()

            exc_obj = C.ClasswordException(physical_nm,
                                           logical_nm)

            G.CLASSWORD_EXCEPTIONS.append(exc_obj)

    G.PHYSICAL_CLASSWORD_EXCEPTION_LIST = list(
        sorted(C.ClasswordException.physical_classword_exception_list.keys()))

    if G.VERBOSE:
        num = len(G.PHYSICAL_CLASSWORD_EXCEPTION_LIST)
        if G.GET_CFG_FROM_GIT:
            source = 'from Git'
        else:
            source = 'locally'

        if num == 1:
            indent(f'Read 1 classword exception {source}.')
        else:
            indent(f'Read {num:5,d} classword exceptions {source}.')


# ===============================================================================
def get_classword_exceptions_GIT():
    '''
    Read the latest cfg records from the Git repo.
    '''

    log_filename = '{0}/{1}.log'.format(
        G.TEMP_DIR,
        os.path.splitext(os.path.basename(__file__))[0])

    os_command = 'wget {0} -O {1} >{2} 2>&1'.format(
        f'{G.GIT_URL}/{C.ClasswordException.cfg_filename_rel}',
        f'{G.SCRIPT_DIR}/{C.ClasswordException.cfg_filename_rel}',
        log_filename)

    try:
        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error(f'Child was terminated by signal {-ret}')
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

        get_classword_exceptions_locally()

    except OSError as e:
        G.LOGGER.error(f'Git-archive execution failed: {e}')
        indent(f'Failed: {os_command}')


# ===============================================================================
def get_cfg_classword_exceptions():
    '''
    First try to read the list of classwords dynamically from the
    Data-Modeler's Postres database.

    If the DM database is down, there is a file backup we can read from..
    Try to read the cfg records from the DMV first.
    If that succeeds, save them locally for the next release.
    Or if that fails, use the local copy to read from.
    '''

    if G.RULES_ENGINE_TYPE == 'ESP_RE':
        # These things are not needed for this rules engine
        return

    # -----------------------------------------------------------------------
    # Only load this list if there are rules that will use it.
    rules_that_need_classword_exceptions = ['r216', 'r003']
    # Technically there are more

    intersection = list(set(rules_that_need_classword_exceptions) &
                        set(G.SHOULD_CHECK_RULE))
    if len(intersection) == 0:
        return

    # -----------------------------------------------------------------------
    if G.GET_CFG_FROM_GIT:
        get_classword_exceptions_GIT()
    else:
        get_classword_exceptions_DMV()

        if len(G.PHYSICAL_CLASSWORD_EXCEPTION_LIST) > 0:

            save_classword_exceptions_locally()

        else:
            get_classword_exceptions_locally()
