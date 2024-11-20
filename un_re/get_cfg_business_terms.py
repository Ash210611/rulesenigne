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
def get_business_terms_DMV_rows():
    '''
    Retrieve the rows from the database.
    '''

    sql = 'select do_not_use_this_nm, use_this_nm, do_not_use_desc ' + \
          'from dmv.valdtn_ref_obj_do_not_use ' + \
          "where do_not_use_this_nm not like 'SRC%' " + \
          'order by do_not_use_this_nm;'

    rows = run_pg_statement(sql)

    return rows


# ===============================================================================
def get_business_terms_DMV():
    '''
    This function will download the business terms
    from the DMV Postgres database
    '''

    rows = get_business_terms_DMV_rows()

    these_business_terms = []

    for row in rows:
        old_term_txt = row[0].strip()
        new_term_txt = row[1].strip()
        comment_txt = row[2].strip()

        this_business_term = C.BusinessTerm(
            old_term_txt,
            new_term_txt,
            comment_txt)

        these_business_terms.append(this_business_term)

    G.BUSINESS_TERM_LIST = list(sorted(these_business_terms))

    if G.VERBOSE:
        num = len(G.BUSINESS_TERM_LIST)
        if num == 1:
            indent('Read 1 business term from the DMV database.')
        else:
            indent('Read {0:5,d} business terms from the DMV database.'.format(num))


# ===============================================================================
def save_business_terms_locally():
    '''
    Save database rows to a local table for disaster recovery.
    '''

    old_term_txt_len = len('old_term_txt')
    new_term_txt_len = len('new_term_txt')
    comment_txt_len = len('comment_txt')

    for rec in G.BUSINESS_TERM_LIST:
        old_term_txt_len = max(old_term_txt_len, len(rec.old_term_txt))
        new_term_txt_len = max(new_term_txt_len, len(rec.new_term_txt))
        comment_txt_len = max(comment_txt_len, len(rec.comment_txt))

    rec_format = '{{0:{0}s}} | {{1:{1}s}} | {{2:{2}s}}'.format(
        old_term_txt_len + 2,  # + 2 for the comment symbol
        new_term_txt_len,
        comment_txt_len)

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.BusinessTerm.cfg_filename_rel)

    with open(cfg_filename, 'w', encoding='utf-8') as cfg_file:

        fprint(cfg_file, '# Filename: {0}'.format(
            cfg_filename.replace(G.SCRIPT_DIR, '$SCRIPT_DIR')))
        fprint(cfg_file, '#')

        rows = get_cfg_table_comment('dmv', 'valdtn_ref_obj_do_not_use')

        for row in rows:
            for line in row[0].split('\n'):
                fprint(cfg_file, f'# {line}')
        fprint(cfg_file, '#')

        fprint(cfg_file, rec_format.format(
            '# ' + 'old_term_txt',
            'new_term_txt',
            'comment_txt'))

        fprint(cfg_file, rec_format.format(
            '# ' + '-' * old_term_txt_len,
            '-' * new_term_txt_len,
            '-' * comment_txt_len))

        for rec in G.BUSINESS_TERM_LIST:
            fprint(cfg_file, rec_format.format(
                rec.old_term_txt,
                rec.new_term_txt,
                rec.comment_txt))


# ===============================================================================
def get_business_terms_locally():
    '''
    Read from a static table.
    '''

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.BusinessTerm.cfg_filename_rel)

    these_business_terms = []

    with open(cfg_filename, 'r', encoding='utf-8') as cfg_file:
        for line in cfg_file.readlines():
            if line.find('#') > -1:
                continue

            line = line.strip()
            old_term_txt, new_term_txt, comment_txt = line.split('|')

            old_term_txt = old_term_txt.strip()
            new_term_txt = new_term_txt.strip()
            comment_txt = comment_txt.strip()

            this_business_term = C.BusinessTerm(
                old_term_txt,
                new_term_txt,
                comment_txt)

            these_business_terms.append(this_business_term)

    G.BUSINESS_TERM_LIST = list(sorted(these_business_terms))

    if G.VERBOSE:
        num = len(G.BUSINESS_TERM_LIST)
        if G.GET_CFG_FROM_GIT:
            source = 'from Git'
        else:
            source = 'locally'

        if num == 1:
            indent(f'Read 1 business term {source}.')
        else:
            indent(f'Read {num:5,d} business terms {source}.')


# ===============================================================================
def get_business_terms_GIT():
    '''
    Read the latest cfg records from the Git repo.
    '''

    log_filename = '{0}/{1}.log'.format(
        G.TEMP_DIR,
        os.path.splitext(os.path.basename(__file__))[0])

    os_command = 'wget {0} -O {1} >{2} 2>&1'.format(
        f'{G.GIT_URL}/{C.BusinessTerm.cfg_filename_rel}',
        f'{G.SCRIPT_DIR}/{C.BusinessTerm.cfg_filename_rel}',
        log_filename)

    try:
        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error(f'Child was terminated by signal {-ret}')
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

        get_business_terms_locally()

    except OSError as e:
        G.LOGGER.error(f'Git-archive execution failed: {e}')
        indent(f'Failed: {os_command}')


# ===============================================================================
def get_cfg_business_terms():
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
        # Those are the rules that check business terms.
        return

    if G.GET_CFG_FROM_GIT:
        get_business_terms_GIT()
    else:
        get_business_terms_DMV()

        if len(G.BUSINESS_TERM_LIST) > 0:

            save_business_terms_locally()

        else:
            get_business_terms_locally()
