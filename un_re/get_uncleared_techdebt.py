# pylint: disable=C0209			# Don't require formatted strings

import os
import time

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.fprint import fprint
from un_re.indent_info import indent_info
from un_re.run_pg_statement import run_pg_statement


# ======== =======================================================================
def get_uncleared_techdebt_from_DB():
    '''
    This function will retrieve the list of files with uncleared techdebt
    Postgres database.

    Uncleared techdebt occurs when:
        - a DDL file is labeled with the TechDebt indicator, and
        - had findings (errors or warnings) that were converted
            to benign notices because of the techdebt label, and
        - succeeded as a file overall, and
        - is not an obsolete file (is still found in GitLab), and
        - happened over a year ago, and
        - has not had a success WITHOUT techdebt since then.

    An exception handler will be used to leave the list of uncleared
    techdebt empty in the event that the source event database is unavailable.
    '''

    sql = 'select  max (current_date - ' + \
          'cast (jenkn_build_ts as date)) as "days_ago", ' + \
          'input_file_nm ' + \
          'from    rulesengine.event e1 ' + \
          "where   rule_set_nm = 'TECHDEBT' " + \
          "and     stat_cd in ('SUCCESS', 'NOTICE') " + \
          'and     jenkn_build_ts < current_date - {0} '.format(G.MAX_UNCLEARED_TECHDEBT_DAYS) + \
          'and		coalesce (is_obsolete, false) = false ' + \
          'and     not exists (' + \
          '		select *' + \
          '		from   rulesengine.event e2' + \
          '		where  e1.proj_nm        = e2.proj_nm' + \
          '		and    e1.input_file_nm  = e2.input_file_nm' + \
          "		and    e2.rule_set_nm   != 'TECHDEBT'" + \
          "		and    e2.stat_cd        = 'SUCCESS'" + \
          '		and    e2.jenkn_build_ts > e1.jenkn_build_ts) ' + \
          'group by ' + \
          '	input_file_nm ' + \
          'order by' + \
          '	1 desc;'

    rows = run_pg_statement(sql)

    these_debts = []

    for row in rows:
        days_ago = row[0]
        input_file_nm = row[1]

        this_debt = C.UnclearedTechdebt(
            days_ago,
            input_file_nm)

        these_debts.append(this_debt)

    # Here is an element useful for testing
    # this_debt = C.UnclearedTechdebt (
    # 		400,
    #		'sql/REQ_CLBRTN_MONTHLY_ACTNBL_HIST.sql')
    # these_debts.append (this_debt)

    # Sort it by input_file_nm
    G.UNCLEARED_TECHDEBT = list(sorted(
        these_debts,
        key=lambda UnclearedTechdebt: UnclearedTechdebt.input_file_nm,
        reverse=False))

    indent_info('Read {0:5,d} Uncleared Techdebt records from the Event database.'.format(
        len(G.UNCLEARED_TECHDEBT)))

    return 0


# ======== =======================================================================
def get_uncleared_techdebt_from_cache(cache_filename):
    with open(cache_filename, 'r', encoding='utf-8') as cache_file:
        for line in cache_file.readlines():
            line = line.strip()
            days_ago, input_file_nm = line.split(',')
            this_debt = C.UnclearedTechdebt(
                days_ago,
                input_file_nm)

            G.UNCLEARED_TECHDEBT.append(this_debt)

    indent_info('Read {0:5,d} Uncleared Techdebt records from the cached file.'.format(
        len(G.UNCLEARED_TECHDEBT)))


# ======== =======================================================================
def put_uncleared_techdebt_to_cache(cache_filename):
    with open(cache_filename, 'w', encoding='utf-8') as cache_file:
        for this_debt in G.UNCLEARED_TECHDEBT:
            fprint(cache_file, '{0},{1}'.format(
                this_debt.days_ago,
                this_debt.input_file_nm))


# ===============================================================================
def get_uncleared_techdebt():
    '''
    If the cache filename is less than a day old, use it, else refresh it.
    '''

    if G.RULES_ENGINE_TYPE in ('DATA_MODEL', 'ESP_RE'):
        # These things are not needed for those rules engines
        return

    if G.GET_CFG_FROM_GIT:
        return
    # That variable would only be set True if the DMV is
    # unavailable, which would make the uncleared techdebt
    # unavailable too.

    cache_filename = G.SCRIPT_DIR + '/un_re/resources/uncleared_techdebt.cache'
    load_from_cache = False

    if os.path.exists(cache_filename):
        cache_time_struct = os.stat(cache_filename)

        cache_age = time.time() - cache_time_struct.st_mtime  # age in seconds

        if cache_age < 7 * 24 * 60 * 60:
            # That would be the number of seconds in 7 days.
            load_from_cache = True

    if load_from_cache:
        get_uncleared_techdebt_from_cache(cache_filename)

    else:
        get_uncleared_techdebt_from_DB()

        put_uncleared_techdebt_to_cache(cache_filename)
