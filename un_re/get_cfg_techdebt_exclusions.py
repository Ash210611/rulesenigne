# pylint: disable=C0209			# Don't require formatted strings.
# pylint: disable=C0325			# Allow parens for clarity

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
def get_techdebt_exclusions_DMV_rows():
    '''
    Retrieve the rows from the database.
    '''

    sql = 'select object_nm, ' + \
          'activation_yyyymmdd_dt ' + \
          'from rulesengine.cfg_techdebt_exclusion ' + \
          'ORDER BY object_nm ASC;'

    rows = run_pg_statement(sql)

    return rows


# ======== =======================================================================
def get_techdebt_exclusions_DMV(current_yyyymmdd_dt):
    '''
    This function will download the techdebt_exclusion records from the DB
    Postgres database
    '''

    rows = get_techdebt_exclusions_DMV_rows()

    these_recs = []

    for row in rows:
        object_nm = row[0]
        activation_yyyymmdd_dt = row[1]

        object_nm = object_nm.strip()
        activation_yyyymmdd_dt = activation_yyyymmdd_dt.strip()

        object_nm = object_nm.upper()

        is_active = (activation_yyyymmdd_dt <= current_yyyymmdd_dt)

        this_record = C.TechdebtExclusion(
            object_nm,
            activation_yyyymmdd_dt,
            is_active)

        these_recs.append(this_record)

    # Sort it by word_len descending
    G.TECHDEBT_EXCLUSION_OBJS = list(sorted(these_recs))

    if G.VERBOSE:
        if len(G.TECHDEBT_EXCLUSION_OBJS) == 1:
            indent('Read {0:5,d} techdebt exclusion from the DMV database.'.format(
                len(G.TECHDEBT_EXCLUSION_OBJS)))
        else:
            indent('Read {0:5,d} techdebt exclusions from the DMV database.'.format(
                len(G.TECHDEBT_EXCLUSION_OBJS)))


# ===============================================================================
def sort_func(e):
    '''
    When we write-out the list of techdebt_exclusions locally, I want them
    to be listed in order of their activation date, so the latest
    exclusions are listed last.

    When checking if a column name is on the list, it won't have an
    activation_yyyymmdd_dt, so the __lt__ function uses the is_active
    attribute
    '''
    return e.activation_yyyymmdd_dt + '|' + e.object_nm


# ===============================================================================
def save_cfg_techdebt_exclusions_locally():
    '''
    Save database rows to a local file for disaster recovery.
    '''

    object_nm_len = len('object_nm_len')
    activation_yyyymmdd_dt_len = len('activation_yyyymmdd_dt_len')

    for rec in G.TECHDEBT_EXCLUSION_OBJS:
        object_nm_len = max(object_nm_len, len(rec.object_nm))
        activation_yyyymmdd_dt_len = max(activation_yyyymmdd_dt_len, len(rec.activation_yyyymmdd_dt))

    rec_format = '{{0:{0}s}} | {{1:{1}s}}'.format(
        object_nm_len + 2,  # + 2 for the comment symbol
        activation_yyyymmdd_dt_len)

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.TechdebtExclusion.cfg_filename_rel)

    with open(cfg_filename, 'w', encoding='utf-8') as cfg_file:

        fprint(cfg_file, f'# Filename: {cfg_filename}')
        fprint(cfg_file, '#')

        rows = get_cfg_table_comment('rulesengine', 'cfg_techdebt_exclusion')

        for row in rows:
            for line in row[0].split('\n'):
                fprint(cfg_file, f'# {line}')
        fprint(cfg_file, '#')

        fprint(cfg_file, rec_format.format(
            '# ' + 'object_nm',
            'activation_yyyymmdd_dt'))

        fprint(cfg_file, rec_format.format(
            '# ' + '-' * object_nm_len,
            '-' * activation_yyyymmdd_dt_len))

        for rec in sorted(G.TECHDEBT_EXCLUSION_OBJS, key=sort_func):
            fprint(cfg_file, rec_format.format(
                rec.object_nm,
                rec.activation_yyyymmdd_dt))


# ===============================================================================
def get_techdebt_exclusions_locally(current_yyyymmdd_dt=None):
    cfg_filename = os.path.join(G.SCRIPT_DIR, C.TechdebtExclusion.cfg_filename_rel)

    G.TECHDEBT_EXCLUSION_OBJS = []
    with open(cfg_filename, 'r', encoding='utf-8') as cfg_file:
        for line in cfg_file.readlines():
            if line.find('#') > -1:
                continue

            (object_nm,
             activation_yyyymmdd_dt) = line.split('|')

            activation_yyyymmdd_dt = activation_yyyymmdd_dt.strip()

            object_nm = object_nm.strip()
            activation_yyyymmdd_dt = activation_yyyymmdd_dt.strip()
            # The comment field is only used for documentation

            # Rule IDs remain lower case.
            object_nm = object_nm.upper()

            is_active = (current_yyyymmdd_dt >= activation_yyyymmdd_dt)

            this_instance = C.TechdebtExclusion(object_nm,
                                                activation_yyyymmdd_dt,
                                                is_active)

            G.TECHDEBT_EXCLUSION_OBJS.append(this_instance)

    if G.VERBOSE:
        num = len(G.TECHDEBT_EXCLUSION_OBJS)
        if G.GET_CFG_FROM_GIT:
            source = 'from Git'
        else:
            source = 'locally'

        if len(G.TECHDEBT_EXCLUSION_OBJS) == 1:
            indent(f'Read 1 techdebt_exclusion {source}.')
        else:
            indent(f'Read {num:5,d} techdebt exclusions {source}.')


# ======== =======================================================================
def get_active_exclusions():
    active_recs = []
    for rec in G.TECHDEBT_EXCLUSION_OBJS:
        if rec.is_active:
            active_recs.append(rec.object_nm)

    G.TECHDEBT_EXCLUSIONS = list(sorted(active_recs))


# ===============================================================================
def get_techdebt_exclusions_GIT(current_yyyymmdd_dt):
    '''
    Read the latest cfg records from the Git repo.
    '''

    log_filename = '{0}/{1}.log'.format(
        G.TEMP_DIR,
        os.path.splitext(os.path.basename(__file__))[0])

    os_command = 'wget {0} -O {1} >{2} 2>&1'.format(
        f'{G.GIT_URL}/{C.Article.cfg_filename_rel}',
        f'{G.SCRIPT_DIR}/{C.Article.cfg_filename_rel}',
        log_filename)

    try:
        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error(f'Child was terminated by signal {-ret}')
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

        get_techdebt_exclusions_locally(current_yyyymmdd_dt)

    except OSError as e:
        G.LOGGER.error(f'Git-archive execution failed: {e}')
        indent(f'Failed: {os_command}')


# ======== =======================================================================
def get_cfg_techdebt_exclusions(current_yyyymmdd_dt=None):
    if G.RULES_ENGINE_TYPE in ('DATA_MODEL', 'ESP_RE'):
        # These things are not needed for this rules engine
        return

    if current_yyyymmdd_dt is None:
        current_yyyymmdd_dt = strftime('%Y%m%d', gmtime())

    if G.GET_CFG_FROM_GIT:
        get_techdebt_exclusions_GIT(current_yyyymmdd_dt)
    else:
        get_techdebt_exclusions_DMV(current_yyyymmdd_dt)

        if len(G.TECHDEBT_EXCLUSION_OBJS) > 0:
            save_cfg_techdebt_exclusions_locally()

        else:
            get_techdebt_exclusions_locally(current_yyyymmdd_dt)

    get_active_exclusions()
