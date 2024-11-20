# pylint: disable=C0209			# Don't require formatted strings

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
def get_classword_datatype_variations_DMV_rows():
    '''
    Retrieve the rows from the database.
    '''

    sql = 'select classword, column_nm, datatype, size, comment_txt ' + \
          'from rulesengine.cfg_classword_datatype_variation;'

    rows = run_pg_statement(sql)

    return rows


# ===============================================================================
def get_classword_datatype_variations_DMV():
    '''
    This function will download the cfg records
    from the DMV Postgres database
    '''

    rows = get_classword_datatype_variations_DMV_rows()

    these_recs = []

    for row in rows:
        classword = row[0].strip()
        column_nm = row[1].strip()
        datatype = row[2].strip()
        size = row[3].strip()
        comment_txt = row[4].strip()

        this_rec = C.ClasswordDatatypeVariation(
            classword,
            column_nm,
            datatype,
            size,
            comment_txt)

        these_recs.append(this_rec)

    G.CLASSWORD_DATATYPE_VARIATIONS = list(sorted(these_recs))

    if G.VERBOSE:
        num = len(G.CLASSWORD_DATATYPE_VARIATIONS)
        if num == 1:
            indent('Read 1 classword datatype variation from the DMV database.')
        else:
            indent('Read {0:5,d} classword datatype variations from the DMV database.'.format(num))


# ===============================================================================
def save_classword_datatype_variations_locally():
    '''
    Save database rows to a local table for disaster recovery.
    '''

    classword_len = len('classword')
    column_nm_len = len('column_nm')
    datatype_len = len('datatype')
    size_len = len('size')
    comment_txt_len = len('comment_txt')

    for rec in G.CLASSWORD_DATATYPE_VARIATIONS:
        classword_len = max(classword_len, len(rec.classword))
        column_nm_len = max(column_nm_len, len(rec.column_nm))
        datatype_len = max(datatype_len, len(rec.datatype))
        size_len = max(size_len, len(rec.size))
        comment_txt_len = max(comment_txt_len, len(rec.comment_txt))

    rec_format = '{{0:{0}s}} | {{1:{1}s}} | {{2:{2}s}} | {{3:{3}s}} | {{4:{4}s}}'.format(
        classword_len + 2,  # + 2 for the comment symbol
        column_nm_len,
        datatype_len,
        size_len,
        comment_txt_len)

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.ClasswordDatatypeVariation.cfg_filename_rel)

    with open(cfg_filename, 'w', encoding='utf-8') as cfg_file:

        fprint(cfg_file, '# Filename: {0}'.format(
            cfg_filename.replace(G.SCRIPT_DIR, '$SCRIPT_DIR')))
        fprint(cfg_file, '#')

        rows = get_cfg_table_comment('rulesengine', 'cfg_classword_datatype_variation')

        for row in rows:
            for line in row[0].split('\n'):
                fprint(cfg_file, f'# {line}')
        fprint(cfg_file, '#')

        fprint(cfg_file, rec_format.format(
            '# ' + 'classword',
            'column_nm',
            'datatype',
            'size',
            'comment_txt'))

        fprint(cfg_file, rec_format.format(
            '# ' + '-' * classword_len,
            '-' * column_nm_len,
            '-' * datatype_len,
            '-' * size_len,
            '-' * comment_txt_len))

        for rec in G.CLASSWORD_DATATYPE_VARIATIONS:
            fprint(cfg_file, rec_format.format(
                rec.classword,
                rec.column_nm,
                rec.datatype,
                rec.size,
                rec.comment_txt))


# ===============================================================================
def get_classword_datatype_variations_locally():
    lst_filename = os.path.join(G.SCRIPT_DIR, C.ClasswordDatatypeVariation.cfg_filename_rel)

    G.CLASSWORD_DATATYPE_VARIATIONS = []
    with open(lst_filename, 'r', encoding='utf-8') as lst_file:
        for line in lst_file.readlines():
            if line.find('#') > -1:
                continue

            (classword, column_nm, datatype, size, comment_txt) = line.split('|')

            classword = classword.strip()
            column_nm = column_nm.strip()
            datatype = datatype.strip()
            size = size.strip()
            comment_txt = comment_txt.strip()

            this_instance = C.ClasswordDatatypeVariation(classword,
                                                         column_nm,
                                                         datatype,
                                                         size,
                                                         comment_txt)

            G.CLASSWORD_DATATYPE_VARIATIONS.append(this_instance)

    if G.VERBOSE:
        num = len(G.CLASSWORD_DATATYPE_VARIATIONS)
        if G.GET_CFG_FROM_GIT:
            source = 'from Git'
        else:
            source = 'locally'

        if num == 1:
            indent(f'Read 1 classword datatype variation {source}.')
        else:
            indent(f'Read {num:5,d} classword datatype variations {source}.')


# ===============================================================================
def get_classword_datatype_variations_GIT():
    '''
    Read the latest cfg records from the Git repo.
    '''

    log_filename = '{0}/{1}.log'.format(
        G.TEMP_DIR,
        os.path.splitext(os.path.basename(__file__))[0])

    os_command = 'wget {0} -O {1} >{2} 2>&1'.format(
        f'{G.GIT_URL}/{C.ClasswordDatatypeVariation.cfg_filename_rel}',
        f'{G.SCRIPT_DIR}/{C.ClasswordDatatypeVariation.cfg_filename_rel}',
        log_filename)

    try:
        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error(f'Child was terminated by signal {-ret}')
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

        get_classword_datatype_variations_locally()

    except OSError as e:
        G.LOGGER.error(f'Git-archive execution failed: {e}')
        indent(f'Failed: {os_command}')


# ===============================================================================
def get_cfg_classword_datatype_variations():
    '''
    Try to read the cfg records from the DMV first.
    If that succeeds, save them locally for the next release.
    Or if that fails, use the local copy to read from.
    '''

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
        get_classword_datatype_variations_GIT()
    else:
        get_classword_datatype_variations_DMV()

        if len(G.CLASSWORD_DATATYPE_VARIATIONS) > 0:

            save_classword_datatype_variations_locally()

        else:
            get_classword_datatype_variations_locally()
