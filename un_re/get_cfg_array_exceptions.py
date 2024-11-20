# pylint: disable=C0209				# Don't require formatted strings.

import os
import subprocess
import sys
from time import gmtime, strftime

import un_re.ERROR_NUMBERS as E
import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.fprint import fprint
from un_re.get_cfg_table_comment import get_cfg_table_comment
from un_re.indent import indent
from un_re.run_pg_statement import run_pg_statement


# ===============================================================================
def get_array_exceptions_DMV_rows():
    '''
    Retrieve the rows from the database.
    '''

    sql = 'select column_nm, expiration_dt, comment_txt ' + \
          'from rulesengine.cfg_array_exception ' + \
          'order by column_nm;'

    rows = run_pg_statement(sql)

    return rows


# ===============================================================================
def get_array_exceptions_DMV(current_yyyymmdd):
    '''
    This function will download the array exceptions
    from the DMV Postgres database
    '''

    rows = get_array_exceptions_DMV_rows()

    these_array_exceptions = []

    for row in rows:
        column_nm = row[0].strip()
        expiration_dt = row[1].strip()
        comment_txt = row[2].strip()

        if current_yyyymmdd > expiration_dt:
            continue

        this_array_exception = C.ArrayException(
            column_nm,
            expiration_dt,
            comment_txt)

        these_array_exceptions.append(this_array_exception)

    G.ARRAY_EXCEPTION_LIST = list(sorted(these_array_exceptions))

    if G.VERBOSE:
        num = len(G.ARRAY_EXCEPTION_LIST)
        if num == 1:
            indent('Read 1 array exception from the DMV database.')
        else:
            indent('Read {0:5,d} array exceptions from the DMV database.'.format(num))


# ===============================================================================
def save_array_exceptions_locally():
    '''
        Save database rows to a local table for disaster recovery.
        '''

    column_nm_len = len('column_nm')
    expiration_dt_len = len('expiration_dt')
    comment_txt_len = len('comment_txt')

    for rec in G.ARRAY_EXCEPTION_LIST:
        column_nm_len = max(column_nm_len, len(rec.column_nm))
        expiration_dt_len = max(expiration_dt_len, len(rec.expiration_dt))
        comment_txt_len = max(comment_txt_len, len(rec.comment_txt))

    rec_format = '{{0:{0}s}} | {{1:{1}s}} | {{2:{2}s}}'.format(
        column_nm_len + 2,
        expiration_dt_len,
        comment_txt_len)

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.ArrayException.cfg_filename_rel)

    with open(cfg_filename, 'w', encoding='utf-8') as cfg_file:

        fprint(cfg_file, '# Filename: {0}'.format(
            cfg_filename.replace(G.SCRIPT_DIR, '$SCRIPT_DIR')))
        fprint(cfg_file, '#')

        rows = get_cfg_table_comment('rulesengine', 'cfg_array_exception')

        for row in rows:
            for line in row[0].split('\n'):
                fprint(cfg_file, f'# {line}')
        fprint(cfg_file, '#')

        fprint(cfg_file, rec_format.format(
            '# ' + 'column_nm',
            'expiration_dt',
            'comment_txt'))

        fprint(cfg_file, rec_format.format(
            '# ' + '-' * column_nm_len,
            '-' * expiration_dt_len,
            '-' * comment_txt_len))

        for rec in G.ARRAY_EXCEPTION_LIST:
            fprint(cfg_file, rec_format.format(
                rec.column_nm,
                rec.expiration_dt,
                rec.comment_txt))


# ===============================================================================
def get_array_exceptions_locally(current_yyyymmdd):
    '''
        Read from a static table.
        '''

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.ArrayException.cfg_filename_rel)

    these_array_exceptions = []

    with open(cfg_filename, 'r', encoding='utf-8') as word_file:
        for line in word_file.readlines():
            if line.find('#') > -1:
                continue

            line = line.strip()
            column_nm, expiration_dt, comment_txt = line.split('|')

            column_nm = column_nm.strip()
            expiration_dt = expiration_dt.strip()

            if current_yyyymmdd > expiration_dt:
                continue

            this_array_exception = C.ArrayException(
                column_nm,
                expiration_dt,
                comment_txt)

            these_array_exceptions.append(this_array_exception)

    G.ARRAY_EXCEPTION_LIST = list(sorted(these_array_exceptions))

    if G.VERBOSE:
        num = len(G.ARRAY_EXCEPTION_LIST)
        if G.GET_CFG_FROM_GIT:
            source = 'from Git'
        else:
            source = 'locally'
        if num == 1:
            indent(f'Read 1 array exception {source}.')
        else:
            indent(f'Read {num:5,d} array exceptions {source}.')


# ===============================================================================
def get_array_exceptions_GIT(current_yyyymmdd):
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

        get_array_exceptions_locally(current_yyyymmdd)

    except OSError as e:
        G.LOGGER.error(f'Git-archive execution failed: {e}')
        indent(f'Failed: {os_command}')


# ===============================================================================
def get_cfg_array_exceptions():
    '''
    Try to read the cfg records from the DMV first.
    If that succeeds, save them locally for the next release.
    Or if that fails, use the local copy to read from.
    '''

    if G.RULES_ENGINE_TYPE == 'ESP_RE':
        # These things are not needed for this rules engine
        return

    if 'r221' not in G.SHOULD_CHECK_RULE:
        # That is the rule that checks array exceptions.
        return

    current_yyyymmdd = strftime('%Y%m%d', gmtime())

    if G.GET_CFG_FROM_GIT:
        get_array_exceptions_GIT(current_yyyymmdd)
    # After retrieving from Git, we don't need to save them
    # locally if we retrieved them from Git to start with.
    else:
        get_array_exceptions_DMV(current_yyyymmdd)

        if len(G.ARRAY_EXCEPTION_LIST) > 0:

            save_array_exceptions_locally()

        else:
            get_array_exceptions_locally(current_yyyymmdd)
