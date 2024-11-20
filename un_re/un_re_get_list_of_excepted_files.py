# pylint: disable=C0209			# Don't require formatted strings

import os

import un_re.global_shared_variables as G


# ===============================================================================
def un_re_get_list_of_excepted_files():
    if G.RULES_ENGINE_TYPE == 'TERADATA_DML':
        exc_filename = os.path.join(G.INPUT_DIR, 'DREML_files_to_skip.lst')
    elif G.RULES_ENGINE_TYPE in ('HIVE_DDL_RE', 'PG_RE', 'SNOWFLAKE',
                                 'DATABRICKS', 'DB2_RE', 'ORE'):

        exc_filename = os.path.join(G.INPUT_DIR, 'UN_RE_files_to_skip.lst')

    else:
        return

    G.EXC_FILENAME_LIST = []
    num_blank_lines = 0

    found = os.path.exists(exc_filename)
    if not found:
        G.LOGGER.info('No exception list was found.')

        if G.VERBOSE:
            G.LOGGER.info('Did not find : {0}'.format(
                exc_filename.replace(G.INPUT_DIR, '$INPUT_DIR')))

    else:
        G.LOGGER.info('Found exception list.')
        G.LOGGER.info(f'Reading: {exc_filename}')

        with open(exc_filename, 'r', encoding='utf-8') as exc_file:
            for line in exc_file.readlines():
                if line.find('#') > -1:
                    continue

                line = line.strip()

                if len(line) > 0:
                    # Do not append blank lines
                    G.EXC_FILENAME_LIST.append(line)
                else:
                    num_blank_lines += 1

    if num_blank_lines > 0:
        G.LOGGER.info(
            'Skipped {0} blank lines in {1}'.format(
                num_blank_lines,
                os.path.basename(exc_filename)))
