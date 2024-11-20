# pylint: disable=C0209				# Don't require foratted strings

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
def get_article_DMV_rows():
    '''
    Retrieve the rows from the database.
    '''

    sql = 'select artcl_word_txt ' + \
          'from dmv.wrk_artcl_word;'

    rows = run_pg_statement(sql)

    return rows


# ===============================================================================
def get_articles_DMV():
    '''
    This function will download the cfg records
    from the DMV Postgres database
    '''

    rows = get_article_DMV_rows()

    these_recs = []

    for row in rows:
        article_nm = row[0].strip()

        this_rec = C.Article(article_nm)

        these_recs.append(this_rec)

    G.ARTICLE_LIST = list(sorted(these_recs))

    if G.VERBOSE:
        num = len(G.ARTICLE_LIST)
        if num == 1:
            indent('Read {0:5,d} article from the DMV database.'.format(num))
        else:
            indent('Read {0:5,d} articles from the DMV database.'.format(num))


# ===============================================================================
def save_articles_locally():
    '''
    Save database rows to a local file for disaster recovery.
    '''

    article_nm_len = len('article_nm')

    for rec in G.ARTICLE_LIST:
        article_nm_len = max(article_nm_len, len(rec.article_nm))

    rec_format = '{{0:{0}s}} | '.format(
        article_nm_len + 2  # + 2 for the comment symbol
    )

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.Article.cfg_filename_rel)

    with open(cfg_filename, 'w', encoding='utf-8') as cfg_file:

        fprint(cfg_file, '# Filename: {0}'.format(
            cfg_filename.replace(G.SCRIPT_DIR, '$SCRIPT_DIR')))
        fprint(cfg_file, '#')

        rows = get_cfg_table_comment('dmv', 'wrk_artcl_word')

        for row in rows:
            for line in row[0].split('\n'):
                fprint(cfg_file, f'# {line}')
        fprint(cfg_file, '#')

        fprint(cfg_file, rec_format.format(
            '# ' + 'article_nm'
        ))

        fprint(cfg_file, rec_format.format(
            '# ' + '-' * article_nm_len
        ))

        for rec in G.ARTICLE_LIST:
            fprint(cfg_file, rec_format.format(
                rec.article_nm
            ))


# ===============================================================================
def get_articles_locally():
    '''
    Read from a local file.
    '''

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.Article.cfg_filename_rel)

    these_recs = []

    with open(cfg_filename, 'r', encoding='utf-8') as cfg_file:
        for line in cfg_file.readlines():
            if line.find('#') > -1:
                continue

            line = line.strip()
            article_nm = line.split('|')[0]

            article_nm = article_nm.strip()

            this_rec = C.Article(article_nm)

            these_recs.append(this_rec)

    G.ARTICLE_LIST = list(sorted(these_recs))

    if G.VERBOSE:
        num = len(G.ARTICLE_LIST)
        if G.GET_CFG_FROM_GIT:
            source = 'from Git'
        else:
            source = 'locally'
        if num == 1:
            indent(f'Read 1 article {source}.')
        else:
            indent(f'Read {num:5,d} articles {source}.')


# ===============================================================================
def get_articles_GIT():
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

        get_articles_locally()

    except OSError as e:
        G.LOGGER.error(f'Git-archive execution failed: {e}')
        indent(f'Failed: {os_command}')


# ===============================================================================
def get_cfg_articles():
    '''
    Try to read the cfg records from the DMV first.
    If that succeeds, save them locally for the next release.
    Or if that fails, use the local copy to read from.
    '''

    if G.RULES_ENGINE_TYPE == 'ESP_RE':
        # These things are not needed for this rules engine
        return

    if 'r219' in G.SHOULD_CHECK_RULE:
        pass
    elif 'r258' in G.SHOULD_CHECK_RULE:
        pass
    else:
        # Those are the rules that check articles
        return

    if G.GET_CFG_FROM_GIT:
        get_articles_GIT()
    else:
        get_articles_DMV()

        if len(G.ARTICLE_LIST) > 0:

            save_articles_locally()

        else:
            get_articles_locally()
