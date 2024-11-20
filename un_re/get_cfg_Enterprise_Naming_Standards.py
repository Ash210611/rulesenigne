# pylint: 	disable=C0209		# Don't require formatted strings

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
def get_ens_DMV_rows():
    '''
    Retrieve the rows from the database.

    Status code .
    ‘A’ –add (new abbreviation)
    ‘D’ – drop  (soft delete)
    ‘M’ – modify (replaced previous abbreviation with a new abbreviation)

    So, use ‘A’ & ‘M’ and ignore ‘D’.
    '''

    sql = 'select distinct bus_term_nm, abbr_txt, alt_abbr_txt ' + \
          'from dmv.entpr_nm_std_2015 ' + \
          "where stat_cd in ('A', 'M') " + \
          'order by bus_term_nm;'

    rows = run_pg_statement(sql)

    return rows


# ======== =======================================================================
def get_Enterprise_Naming_Standards_DMV():
    '''
    This function will download the Enterprise Naming Standards from the DMV
    Postgres database
    '''

    rows = get_ens_DMV_rows()

    these_recs = []

    for row in rows:
        bus_term_nm = row[0]  # aka 'word' in my class object
        abbr_txt = row[1]
        alt_abbr_txt = row[2]

        this_abbreviation = C.Abbreviation(
            bus_term_nm,
            abbr_txt)

        # Always append the primary abbreviation
        these_recs.append(this_abbreviation)

        # Don't list alternative abbreviations that are empty or None
        if alt_abbr_txt is None:
            pass
        else:
            alt_abbr_txt = alt_abbr_txt.strip()
            if alt_abbr_txt != '':
                alt_abbreviation = C.Abbreviation(
                    bus_term_nm,
                    alt_abbr_txt)

                these_recs.append(alt_abbreviation)

    # Cast as a set to remove the duplicates
    # unique_set = set (these_recs)
    # No, I think it will be better to remove duplicates using Select Distinct

    # Convert it back to a list for convenient access
    # these_recs = list (unique_set)

    # Sort it by word_len descending
    G.ENTERPRISE_NAMING_STANDARD = list(sorted(these_recs))

    if G.VERBOSE:
        num = len(G.ENTERPRISE_NAMING_STANDARD)
        if num == 1:
            indent('Read 1 Standard Enterprise Name from the DMV database.')
        else:
            indent('Read {0:5,d} Standard Enterprise names from the DMV database.'.format(num))


# ===============================================================================
def save_ens_locally():
    '''
    Save database rows to a local file for disaster recovery.
    '''

    word_len = len('word')
    abbr_len = len('abbr')

    for rec in G.ENTERPRISE_NAMING_STANDARD:
        word_len = max(word_len, len(rec.word))
        abbr_len = max(abbr_len, len(rec.abbr))

    rec_format = '{{0:{0}s}} | {{1:{1}s}}'.format(
        word_len + 2,  # + 2 for the comment symbol
        abbr_len
    )

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.Abbreviation.cfg_filename_rel)

    with open(cfg_filename, 'w', encoding='utf-8') as cfg_file:

        fprint(cfg_file, '# Filename: {0}'.format(
            cfg_filename.replace(G.SCRIPT_DIR, '$SCRIPT_DIR')))
        fprint(cfg_file, '#')

        rows = get_cfg_table_comment('dmv', 'entpr_nm_std_2015')

        # Print the table comment that explains what this table is for.
        for row in rows:
            for line in row[0].split('\n'):
                fprint(cfg_file, f'# {line}')
        fprint(cfg_file, '#')

        # Print the column headings, as if this text file had columns
        fprint(cfg_file, rec_format.format(
            '# ' + 'word',
            'abbr'
        ))
        fprint(cfg_file, rec_format.format(
            '# ' + '-' * word_len,
            '-' * abbr_len
        ))

        # Print the actual abbreviations
        for rec in G.ENTERPRISE_NAMING_STANDARD:
            fprint(cfg_file, rec_format.format(
                rec.word,
                rec.abbr
            ))


# ===============================================================================
def get_ens_locally():
    '''
    Read from a static table.
    '''

    cfg_filename = os.path.join(G.SCRIPT_DIR, C.Abbreviation.cfg_filename_rel)

    these_recs = []

    with open(cfg_filename, 'r', encoding='utf-8') as cfg_file:
        for line in cfg_file.readlines():
            if line.find('#') > -1:
                continue

            word = line.split('|')[0]
            abbr = line.split('|')[1]

            word = word.strip()
            abbr = abbr.strip()

            this_rec = C.Abbreviation(word, abbr)

            these_recs.append(this_rec)

    G.ENTERPRISE_NAMING_STANDARD = list(sorted(these_recs))

    if G.VERBOSE:
        num = len(G.ENTERPRISE_NAMING_STANDARD)
        if G.GET_CFG_FROM_GIT:
            source = 'from Git'
        else:
            source = 'locally'

        if num == 1:
            indent(f'Read 1 Standard Enterprise Name {source}.')
        else:
            indent(f'Read {num:5,d} Standard Enterprise names {source}.')


# ======== =======================================================================
def separate_abbreviation_types():
    '''
    Separate the abbreviations with multiple tokens from the ones with
    single tokens.  The Multi-token list must be searched linearly, and at
    least it will be shorter.   The Single-token list can use a
    binary search.
    '''

    multi_tokens = []
    single_tokens = []

    for abbreviation in G.ENTERPRISE_NAMING_STANDARD:

        if abbreviation.isa_multi_token_abbreviation:
            new_abbr = C.AbbreviatedMultiToken(
                abbreviation.word,
                abbreviation.abbr)
            multi_tokens.append(new_abbr)
        else:
            new_abbr = C.AbbreviatedSingleToken(
                abbreviation.word,
                abbreviation.abbr)
            single_tokens.append(new_abbr)

    G.ABBREVIATED_MULTI_TOKENS = list(sorted(multi_tokens))
    G.ABBREVIATED_SINGLE_TOKENS = list(sorted(single_tokens))


# ===============================================================================
def get_Enterprise_Naming_Standards_GIT():
    '''
    Read the latest cfg records from the Git repo.
    '''

    log_filename = '{0}/{1}.log'.format(
        G.TEMP_DIR,
        os.path.splitext(os.path.basename(__file__))[0])

    os_command = 'wget {0} -O {1} >{2} 2>&1'.format(
        f'{G.GIT_URL}/{C.Abbreviation.cfg_filename_rel}',
        f'{G.SCRIPT_DIR}/{C.Abbreviation.cfg_filename_rel}',
        log_filename)

    try:
        ret = subprocess.call(os_command, shell=True)

        if ret < 0:
            G.LOGGER.error(f'Child was terminated by signal {-ret}')
            sys.exit(E.CHILD_TERMINATED_BY_SIGNAL)

        get_ens_locally()

    except OSError as e:
        G.LOGGER.error(f'Git-archive execution failed: {e}')
        indent(f'Failed: {os_command}')


# ======== =======================================================================
def get_cfg_Enterprise_Naming_Standards():
    if G.RULES_ENGINE_TYPE == 'ESP_RE':
        # These things are not needed for this rules engine
        return

    if 'r303' not in G.SHOULD_CHECK_RULE:
        # That is the rules that checks abbreviations.
        return

    if G.GET_CFG_FROM_GIT:
        get_Enterprise_Naming_Standards_GIT()
    else:
        get_Enterprise_Naming_Standards_DMV()

        if len(G.ENTERPRISE_NAMING_STANDARD) > 0:

            save_ens_locally()

        else:
            get_ens_locally()

    separate_abbreviation_types()
