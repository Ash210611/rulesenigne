# pylint: disable=C0209				# Don't require formatted strings.

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
def get_multiset_base_tables_DMV_rows():
    '''
    Retrieve the rows from the database.
    '''

    sql = 'select table_nm, comment_txt ' + \
          'from rulesengine.cfg_multiset_base_table ' + \
          'order by table_nm;'

    rows = run_pg_statement(sql)

    return rows


# ===============================================================================
def get_multiset_base_tables_DMV():
    '''
    This function will download the multiset_base_tables
    from the DMV Postgres database
    '''

    rows = get_multiset_base_tables_DMV_rows()

    these_multiset_base_tables = []

    for row in rows:
        table_nm = row[0].strip()
        comment_txt = row[1].strip()

        this_multiset_base_table = C.MultisetBaseTable(
            table_nm,
            comment_txt)

        these_multiset_base_tables.append(this_multiset_base_table)

    G.MULTISET_BASE_TABLES = list(sorted(these_multiset_base_tables))

    if G.VERBOSE:
        num = len(G.MULTISET_BASE_TABLES)
        if num == 1:
            indent('Read 1 multiset base table from the DMV database.')
        else:
            indent('Read {0:5,d} multiset base tables from the DMV database.'.format(num))


# ===============================================================================
def save_multiset_base_tables_locally():
    '''
    Save database rows to a local table for disaster recovery.
    '''

    table_nm_len = len('table_nm')
    comment_txt_len = len('comment_txt')

    for rec in G.MULTISET_BASE_TABLES:
        table_nm_len = max(table_nm_len, len(rec.table_nm))
        comment_txt_len = max(comment_txt_len, len(rec.comment_txt))

    rec_format = '{{0:{0}s}} | {{1:{1}s}}'.format(
        table_nm_len + 2,  # + 2 for the comment symbol
        comment_txt_len)

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.MultisetBaseTable.cfg_filename_rel)

    with open(cfg_filename, 'w', encoding='utf-8') as cfg_file:

        fprint(cfg_file, '# Filename: {0}'.format(
            cfg_filename.replace(G.SCRIPT_DIR, '$SCRIPT_DIR')))
        fprint(cfg_file, '#')

        rows = get_cfg_table_comment('rulesengine', 'cfg_multiset_base_table')

        for row in rows:
            for line in row[0].split('\n'):
                fprint(cfg_file, f'# {line}')
        fprint(cfg_file, '#')

        fprint(cfg_file, rec_format.format(
            '# ' + 'table_nm',
            'comment_txt'))

        fprint(cfg_file, rec_format.format(
            '# ' + '-' * table_nm_len,
            '-' * comment_txt_len))

        for rec in G.MULTISET_BASE_TABLES:
            fprint(cfg_file, rec_format.format(
                rec.table_nm,
                rec.comment_txt))


# ===============================================================================
def get_multiset_base_tables_locally():
    '''
    Read from a static table.
    '''

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.MultisetBaseTable.cfg_filename_rel)

    these_multiset_base_tables = []

    with open(cfg_filename, 'r', encoding='utf-8') as cfg_file:
        for line in cfg_file.readlines():
            if line.find('#') > -1:
                continue

            line = line.strip()
            table_nm, comment_txt = line.split('|')

            table_nm = table_nm.strip()
            comment_txt = comment_txt.strip()

            this_multiset_base_table = C.MultisetBaseTable(
                table_nm,
                comment_txt)

            these_multiset_base_tables.append(this_multiset_base_table)

    G.MULTISET_BASE_TABLES = list(sorted(these_multiset_base_tables))

    if G.VERBOSE:
        num = len(G.MULTISET_BASE_TABLES)
        if G.GET_CFG_FROM_GIT:
            source = 'from Git'
        else:
            source = 'locally'

        if num == 1:
            indent(f'Read 1 multiset base table {source}.')
        else:
            indent(f'Read {num:5,d} multiset base tables {source}.')


# ===============================================================================
def get_multiset_base_tables_GIT():
    '''
    Read the latest cfg records from the Git repo.
    '''

    log_filename = '{0}/{1}.log'.format(
        G.TEMP_DIR,
        os.path.splitext(os.path.basename(__file__))[0])

    os_command = 'wget {0} -O {1} >{2} 2>&1'.format(
        f'{G.GIT_URL}/{C.MultisetBaseTable.cfg_filename_rel}',
        f'{G.SCRIPT_DIR}/{C.MultisetBaseTable.cfg_filename_rel}',
        log_filename)

    try:
        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error(f'Child was terminated by signal {-ret}')
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

        get_multiset_base_tables_locally()

    except OSError as e:
        G.LOGGER.error(f'Git-archive execution failed: {e}')
        indent(f'Failed: {os_command}')


# ===============================================================================
def get_cfg_multiset_base_tables():
    """
    For now this is reading from a static table.
    In the long-term this should be read dynamically from the Data-Modeler's
    Postres database.
    """

    if 'r213' in G.SHOULD_CHECK_RULE:
        pass
    elif 'r253' in G.SHOULD_CHECK_RULE:
        pass
    else:
        return

    if G.GET_CFG_FROM_GIT:
        get_multiset_base_tables_GIT()
    else:
        get_multiset_base_tables_DMV()

        if len(G.MULTISET_BASE_TABLES) > 0:

            save_multiset_base_tables_locally()

        else:
            get_multiset_base_tables_locally()
