# pylint: disable=C0209			# Don't require formatted strings.

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
def get_rules_exceptions_DB_rows():
    '''
    Retrieve the rows from the database.
    '''

    sql = 'select rule_id, project_nm, table_nm, column_nm, ' + \
          'exp_yyyymmdd_dt, comment_txt ' + \
          'from rulesengine.cfg_rules_exception ' + \
          'ORDER BY rule_id ASC, project_nm ASC, table_nm ASC, column_nm ASC;'

    rows = run_pg_statement(sql)

    return rows


# ======== =======================================================================
def get_rules_exceptions_DB():
    '''
    This function will download the rules_exception records from the DB
    Postgres database
    '''

    current_yyyymmdd_dt = strftime('%Y%m%d', gmtime())

    rows = get_rules_exceptions_DB_rows()

    these_recs = []

    for row in rows:
        rule_id = row[0]  # aka 'word' in my class object
        project_nm = row[1]
        table_nm = row[2]
        column_nm = row[3]
        exp_yyyymmdd_dt = row[4]
        comment_txt = row[5]

        rule_id = rule_id.strip()
        project_nm = project_nm.strip()
        table_nm = table_nm.strip()
        column_nm = column_nm.strip()
        comment_txt = comment_txt.strip()

        project_nm = project_nm.upper()
        table_nm = table_nm.upper()
        column_nm = column_nm.upper()
        exp_yyyymmdd_dt = exp_yyyymmdd_dt.upper()

        if exp_yyyymmdd_dt == 'NONE':
            exp_yyyymmdd_dt = '20990101'

        this_record = C.RulesException(
            rule_id,
            project_nm,
            table_nm,
            column_nm,
            exp_yyyymmdd_dt,
            comment_txt)

        if current_yyyymmdd_dt > exp_yyyymmdd_dt:
            this_record.is_expired = True
        else:
            this_record.is_expired = False

        these_recs.append(this_record)

    # Cast as a set to remove the duplicates
    unique_set = set(these_recs)

    # Convert it back to a list for convenient access
    these_recs = list(unique_set)

    # Sort it by word_len descending
    G.RULES_EXCEPTION = list(sorted(these_recs))

    if G.VERBOSE:
        if len(G.RULES_EXCEPTION) == 1:
            indent('Read {0:5,d} rules exception from the DMV database.'.format(
                len(G.RULES_EXCEPTION)))
        else:
            indent('Read {0:5,d} rules exceptions from the DMV database.'.format(
                len(G.RULES_EXCEPTION)))


# ===============================================================================
def save_rules_exceptions_locally():
    '''
    Save database rows to a local file for disaster recovery.
    '''

    rule_id_len = len('rule_id')
    project_nm_len = len('project_nm_len')
    table_nm_len = len('table_nm_len')
    column_nm_len = len('column_nm_len')
    exp_yyyymmdd_dt_len = len('exp_yyyymmdd_dt_len')
    comment_txt_len = len('comment_txt_len')

    for rec in G.RULES_EXCEPTION:
        rule_id_len = max(rule_id_len, len(rec.rule_id))
        project_nm_len = max(project_nm_len, len(rec.project_nm))
        table_nm_len = max(table_nm_len, len(rec.table_nm))
        column_nm_len = max(column_nm_len, len(rec.column_nm))
        exp_yyyymmdd_dt_len = max(exp_yyyymmdd_dt_len, len(rec.exp_yyyymmdd_dt))
        comment_txt_len = max(comment_txt_len, len(rec.comment_txt))

    rec_format = '{{0:{0}s}} | {{1:{1}s}} | {{2:{2}s}} | {{3:{3}s}} | {{4:{4}s}} | {{5:{5}s}}'.format(
        rule_id_len + 2,  # + 2 for the comment symbol
        project_nm_len,
        table_nm_len,
        column_nm_len,
        exp_yyyymmdd_dt_len,
        comment_txt_len)

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.RulesException.cfg_filename_rel)

    with open(cfg_filename, 'w', encoding='utf-8') as cfg_file:

        fprint(cfg_file, f'# Filename: {cfg_filename}')
        fprint(cfg_file, '#')

        if not G.GET_CFG_FROM_GIT:
            rows = get_cfg_table_comment('rulesengine', 'cfg_rules_exception')

        for row in rows:
            for line in row[0].split('\n'):
                fprint(cfg_file, f'# {line}')
        fprint(cfg_file, '#')

        fprint(cfg_file, rec_format.format(
            '# ' + 'rule_id',
            'project_nm',
            'table_nm',
            'column_nm',
            'exp_yyyymmdd_dt',
            'comment_txt'))

        fprint(cfg_file, rec_format.format(
            '# ' + '-' * rule_id_len,
            '-' * project_nm_len,
            '-' * table_nm_len,
            '-' * column_nm_len,
            '-' * exp_yyyymmdd_dt_len,
            '-' * comment_txt_len))

        for rec in G.RULES_EXCEPTION:
            tmp_exp_yyyymmdd_dt = rec.exp_yyyymmdd_dt
            if tmp_exp_yyyymmdd_dt == '20990101':
                tmp_exp_yyyymmdd_dt = 'None'

            fprint(cfg_file, rec_format.format(
                rec.rule_id,
                rec.project_nm,
                rec.table_nm,
                rec.column_nm,
                tmp_exp_yyyymmdd_dt,
                rec.comment_txt))


# ===============================================================================
def get_rules_exceptions_locally(current_yyyymmdd_dt=None):
    cfg_filename = os.path.join(G.SCRIPT_DIR, C.RulesException.cfg_filename_rel)

    if current_yyyymmdd_dt is None:
        current_yyyymmdd_dt = strftime('%Y%m%d', gmtime())

    G.RULES_EXCEPTION = []
    with open(cfg_filename, 'r', encoding='utf-8') as cfg_file:
        for line in cfg_file.readlines():
            if line.find('#') > -1:
                continue

            (rule_id, project_nm, table_nm, column_nm,
             exp_yyyymmdd_dt, comment_txt) = line.split('|')

            exp_yyyymmdd_dt = exp_yyyymmdd_dt.strip()

            if exp_yyyymmdd_dt.upper() == 'NONE':
                exp_yyyymmdd_dt = '20990101'

            rule_id = rule_id.strip()
            project_nm = project_nm.strip()
            table_nm = table_nm.strip()
            column_nm = column_nm.strip()
            comment_txt = comment_txt.strip()
            # The comment field is only used for documentation

            # Rule IDs remain lower case.
            project_nm = project_nm.upper()
            table_nm = table_nm.upper()
            column_nm = column_nm.upper()

            this_instance = C.RulesException(rule_id, project_nm,
                                             table_nm,
                                             column_nm,
                                             exp_yyyymmdd_dt,
                                             comment_txt)

            if current_yyyymmdd_dt > exp_yyyymmdd_dt:
                this_instance.is_expired = True
            else:
                this_instance.is_expired = False

            G.RULES_EXCEPTION.append(this_instance)

    if G.VERBOSE:
        num = len(G.RULES_EXCEPTION)
        if G.GET_CFG_FROM_GIT:
            source = 'from Git'
        else:
            source = 'locally'

        if num == 1:
            indent('Read 1 rules exception {source}.')
        else:
            indent(f'Read {num:5,d} rules exceptions {source}.')


# ===============================================================================
def get_rules_exceptions_GIT():
    '''
    Read the latest cfg records from the Git repo.
    '''

    log_filename = '{0}/{1}.log'.format(
        G.TEMP_DIR,
        os.path.splitext(os.path.basename(__file__))[0])

    os_command = 'wget {0} -O {1} >{2} 2>&1'.format(
        f'{G.GIT_URL}/{C.RulesException.cfg_filename_rel}',
        f'{G.SCRIPT_DIR}/{C.RulesException.cfg_filename_rel}',
        log_filename)

    try:
        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error(f'Child was terminated by signal {-ret}')
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

        get_rules_exceptions_locally()

    except OSError as e:
        G.LOGGER.error(f'Git-archive execution failed: {e}')
        indent(f'Failed: {os_command}')


# ======== =======================================================================
def get_cfg_rules_exceptions():
    if G.RULES_ENGINE_TYPE == 'ESP_RE':
        # These things are not needed for this rules engine
        return

    if G.GET_CFG_FROM_GIT:
        get_rules_exceptions_GIT()
    else:
        get_rules_exceptions_DB()

        if len(G.RULES_EXCEPTION) > 0:

            save_rules_exceptions_locally()

        else:
            get_rules_exceptions_locally()
