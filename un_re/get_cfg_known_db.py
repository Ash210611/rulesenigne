# pylint: disable=C0209			# Don't require formatted strings.
# pylint: disable=R0914			# Too many local variables
# pylint: disable=C0325			# Allow extra parentheses for clarity

import os
import subprocess
import sys

import un_re.ERROR_NUMBERS as E
import un_re.KNOWN_DB as A
import un_re.global_shared_variables as G
from un_re.fprint import fprint
from un_re.get_cfg_table_comment import get_cfg_table_comment
from un_re.indent import indent
from un_re.run_pg_statement import run_pg_statement


# ===============================================================================
def get_known_db_DB_rows():
    '''
    Retrieve the rows from the database.
    '''

    sql = 'select database_basename, database_viewdb_name, ' + \
          'change_from, change_to, ' + \
          'isa_base_db, isa_one_to_one_db, create_svc_view ' + \
          'from rulesengine.cfg_known_db ' + \
          'order by length (database_basename) desc, ' + \
          '    database_basename;'

    rows = run_pg_statement(sql)

    return rows


# ======== =======================================================================
def get_known_db_DMV():
    '''
    This function will download the from the DMV Postgres database
    '''

    rows = get_known_db_DB_rows()

    for row in rows:
        f1 = row[0].strip()
        f2 = row[1].strip()
        f3 = row[2].strip()
        f4 = row[3].strip()
        f5 = (row[4].strip() == 'True')
        f6 = (row[5].strip() == 'True')
        f7 = (row[6].strip() == 'True')

        MyRow = A.MyStruct(f1, f2, f3, f4, f5, f6, f7)

        A.KNOWN_DB.append(MyRow)

    if G.VERBOSE:
        if len(A.KNOWN_DB) == 1:
            indent('Read 1 Known Database from the DMV database.')
        else:
            indent('Read {0:5,d} Known Databases from the DMV database.'.format(
                len(A.KNOWN_DB)))


# ===============================================================================
def print_known_db_column_headings(cfg_file, headings, underscores):
    fprint(cfg_file, '#')
    fprint(cfg_file, headings)
    fprint(cfg_file, underscores)


# ===============================================================================
def save_known_db_locally():
    '''
    Save database rows to a local file for disaster recovery.
    '''

    f1_len = len('database_base')
    f2_len = len('view_database_base')
    f3_len = len('change_database_from')
    f4_len = len('change_database_to')
    f5_len = len('isa_base_db')
    f6_len = len('isa_one_to_one_db')
    f7_len = len('create_svc_view')

    for rec in A.KNOWN_DB:
        f1_len = max(f1_len, len(rec.database_base))
        f2_len = max(f2_len, len(rec.view_database_base))
        f3_len = max(f3_len, len(rec.change_database_from))
        f4_len = max(f4_len, len(rec.change_database_to))
        f5_len = max(f5_len, len(str(rec.isa_base_db)))
        f6_len = max(f6_len, len(str(rec.isa_one_to_one_db)))
        f7_len = max(f7_len, len(str(rec.create_svc_view)))

    rec_format = '{{0:{0}s}} | {{1:{1}s}} | {{2:{2}s}} | {{3:{3}s}} | {{4:{4}s}} | {{5:{5}s}} | {{6:{6}s}}'.format(
        f1_len + 2,  # + 2 for the comment symbol
        f2_len,
        f3_len,
        f4_len,
        f5_len,
        f6_len,
        f7_len)

    cfg_filename = os.path.join(G.SCRIPT_DIR, A.cfg_filename_rel)

    with open(cfg_filename, 'w', encoding='utf-8') as cfg_file:

        fprint(cfg_file, f'# Filename: {cfg_filename}')
        fprint(cfg_file, '#')

        rows = get_cfg_table_comment('rulesengine', 'cfg_known_db')

        for row in rows:
            for line in row[0].split('\n'):
                fprint(cfg_file, f'# {line}')

        headings = rec_format.format(
            '# ' + 'database_base',
            'view_database_base',
            'change_database_from',
            'change_database_to',
            'isa_base_db',
            'isa_one_to_one_db',
            'create_svc_view')

        underscores = rec_format.format(
            '# ' + '-' * f1_len,
            '-' * f2_len,
            '-' * f3_len,
            '-' * f4_len,
            '-' * f5_len,
            '-' * f6_len,
            '-' * f7_len)

        for rec_num, rec in enumerate(A.KNOWN_DB):
            if rec_num % 20 == 0:
                print_known_db_column_headings(cfg_file, headings, underscores)

            fprint(cfg_file, rec_format.format(
                rec.database_base,
                rec.view_database_base,
                rec.change_database_from,
                rec.change_database_to,
                str(rec.isa_base_db),
                str(rec.isa_one_to_one_db),
                str(rec.create_svc_view)))


# ===============================================================================
def get_known_db_locally():
    cfg_filename = os.path.join(G.SCRIPT_DIR, A.cfg_filename_rel)

    with open(cfg_filename, 'r', encoding='utf-8') as cfg_file:
        for line in cfg_file.readlines():
            if line.find('#') > -1:
                continue

            (f1, f2, f3, f4, f5, f6, f7) = line.split('|')

            f1 = f1.strip()
            f2 = f2.strip()
            f3 = f3.strip()
            f4 = f4.strip()
            f5 = (f5.strip() == 'True')
            f6 = (f6.strip() == 'True')
            f7 = (f7.strip() == 'True')

            MyRow = A.MyStruct(f1, f2, f3, f4, f5, f6, f7)

            A.KNOWN_DB.append(MyRow)

    if G.VERBOSE:
        num = len(A.KNOWN_DB)
        if G.GET_CFG_FROM_GIT:
            source = 'from Git'
        else:
            source = 'locally'

        if num == 1:
            indent(f'Read 1 Known Database {source}.')
        else:
            indent(f'Read {num:5,d} Known Databases {source}.')


# ===============================================================================
def get_known_db_GIT():
    '''
    Read the latest cfg records from the Git repo.
    '''

    log_filename = '{0}/{1}.log'.format(
        G.TEMP_DIR,
        os.path.splitext(os.path.basename(__file__))[0])

    os_command = 'wget {0} -O {1} >{2} 2>&1'.format(
        f'{G.GIT_URL}/{A.cfg_filename_rel}',
        f'{G.SCRIPT_DIR}/{A.cfg_filename_rel}',
        log_filename)

    try:
        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error(f'Child was terminated by signal {-ret}')
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

        get_known_db_locally()

    except OSError as e:
        G.LOGGER.error(f'Git-archive execution failed: {e}')
        indent(f'Failed: {os_command}')


# ======== =======================================================================
def get_cfg_known_db():
    if G.GET_CFG_FROM_GIT:
        get_known_db_GIT()
    else:
        get_known_db_DMV()

        if len(A.KNOWN_DB) > 0:

            save_known_db_locally()

        else:
            get_known_db_locally()
