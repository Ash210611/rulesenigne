# pylint: disable=C0209           # Don't require formtted strings

import os

import un_re.global_shared_variables as G
from un_re.indent import indent


# ===============================================================================
def display_summary_message():
    """
    If errors or warnings were reported then display the path to the
    results summary.

    """

    G.LOGGER.info('=' * 88)
    ret = 0
    found_errors = False
    found_warnings = False

    if len(G.ERROR_FILENAME) > 0 and \
            os.path.exists(G.ERROR_FILENAME):

        found_errors = True

        indent('Notice:  One or more errors were found.')
        indent('For a summary of all errors, see:')
        indent('{0}'.format(G.ERROR_FILENAME.replace(G.TEMP_DIR, '$TEMP_DIR')))
        G.LOGGER.info('')

        G.LOGGER.info('For convenience, the contents of that file are:')
        with open(G.ERROR_FILENAME, 'r', encoding='utf-8') as err_file:
            for line in err_file.readlines():
                line = line.strip()
                # Don't display the JUnit line though.
                # That belongs in the JUnit.output.xml file
                if line.find('JUnit') == -1:
                    G.LOGGER.info(line)

            G.LOGGER.info('')

        # Please do not change this exit code, as the pipeline will
        # use that to recognize that errors have occurred.
        ret = 68

    if len(G.WARNING_FILENAME) > 0 and \
            os.path.exists(G.WARNING_FILENAME):

        found_warnings = True

        indent('Notice:  One or more warnings were found.')
        indent('For a summary of all warnings, see:')
        indent('{0}'.format(G.WARNING_FILENAME.replace(G.TEMP_DIR, '$TEMP_DIR')))
        G.LOGGER.info('')

        G.LOGGER.info('For convenience, the contents of that file are:')
        with open(G.WARNING_FILENAME, 'r', encoding='utf-8') as warn_file:
            for line in warn_file.readlines():
                line = line.strip()
                # Don't display the JUnit line though.
                # That belongs in the JUnit.output.xml file
                if line.find('JUnit') == -1:
                    G.LOGGER.info(line)

            G.LOGGER.info('')

    if G.VERBOSE:
        indent('The build log is here:')
        indent(G.LOG_FILENAME.replace(G.TEMP_DIR, '$TEMP_DIR'))

        if not found_errors and not found_warnings:
            indent('Good         : No errors or warnings were reported from the Rules Engine.')

    return ret
