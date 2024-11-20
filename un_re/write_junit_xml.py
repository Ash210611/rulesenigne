# pylint: disable=C0209			# Don't require formatted strings
# pylint: disable=W0702			# Allow bare excepts

import os
import re

import junitparser as jp  # type: ignore

import un_re.global_shared_variables as G


# ===============================================================================
# Adapting junitparserver to produce the JUnit output report.
#
# See also:
#     https://pypi.org/project/junitparser/
# Example usage by C. Finnell:
#     http://git.sys.cigna.com/imdevops/pvs-testing-automation/blob/dev/\
#		Pipeline_IMPVS_INF_Metrics/collect_informatica_metrics.py#L136
#
# In HIVE_DDL_RE, a test case will occur for the combination of each input DML file
# plus each rule.  Test results cannot be saved in memory, because they 
# run in a child processes with no ability to update the parent, so the 
# results are read from the two output files for errors and warnings.
#
# ===============================================================================
def valid_xml_char_ordinal(c):
    '''
    Adapting this function from:
        https://stackoverflow.com/questions/8733233/filtering-out-certain-bytes-in-python
    after a certain DDL file threw this error:
        ValueError: All strings must be XML compatible: Unicode or ASCII, no NULL bytes or control characters
    '''

    codepoint = ord(c)
    # conditions ordered by presumed frequency
    return (
            0x20 <= codepoint <= 0xD7FF or
            codepoint in (0x9, 0xA, 0xD) or
            0xE000 <= codepoint <= 0xFFFD or
            0x10000 <= codepoint <= 0x10FFFF
    )


# ===============================================================================
def append_junit_line(junit_line, sql_statement):
    junit_line = junit_line.strip()

    # (label, severity, file_num, input_filename_rel, msg) = junit_line.split ('|')
    (_, severity, file_num, input_filename_rel, msg) = junit_line.split('|')

    test_case = jp.TestCase(input_filename_rel)
    try:
        test_case.system_out = 'File_num: {0}\n{1}\n'.format(
            file_num,
            sql_statement)
    except ValueError:
        cleaned_string = ''.join(c for c in sql_statement if valid_xml_char_ordinal(c))
        test_case.system_out = 'File_num: {0}\n{1}\n'.format(
            file_num,
            cleaned_string)

    if severity == 'ERROR':
        test_case.result = [jp.Error(msg)]
    else:
        test_case.result = [jp.Failure(msg)]

    return test_case


# ===============================================================================
def write_junit_xml():
    """
    In the JUNIT_DAT_FILENAME, the first line will start with 'JUnit'.
    Subsequent lines will hold the SQL statement corresponding to that
    JUnit finding.
    A SQL statement could have multiple lines, and it likely does, so keep
    reading until you see a line that starts with 'END_SQL'.
    When the END_SQL token is recognized, construct the test_case
    record at that time.
    """

    G.LOGGER.info('Writing findings to the {0} file...'.format(
        os.path.basename(G.JUNIT_XML_FILENAME)))

    num_findings = 0
    test_suite = jp.TestSuite('UN_RE Test Results')

    sql_statement = ''
    if os.path.exists(G.JUNIT_DAT_FILENAME):
        with open(G.JUNIT_DAT_FILENAME, "r", encoding='utf-8') as dat_file:
            for line in dat_file.readlines():
                if line.find('JUnit') > -1:
                    junit_line = line
                elif re.search('^END_SQL', line):
                    num_findings += 1
                    test_suite.add_testcase(append_junit_line(
                        junit_line,
                        sql_statement))
                    if num_findings == 1000:
                        # Stop the madness.  1000 is plenty.
                        break
                    sql_statement = ''
                else:
                    sql_statement += line

    if num_findings == 0:
        test_case = jp.TestCase('No errors or Warnings were found.')
        test_case.result = [jp.Skipped()]
        test_suite.add_testcase(test_case)

    xml = jp.JUnitXml()
    xml.add_testsuite(test_suite)
    try:
        xml.write(G.JUNIT_XML_FILENAME)
    except:
        G.LOGGER.error('Failed to write to {0}.'.format(G.JUNIT_XML_FILENAME))
        G.LOGGER.error('See DAT file for more info: {0}.'.format(G.JUNIT_DAT_FILENAME))

    if num_findings == 1:
        G.LOGGER.info('Wrote {0} finding to the {1} file.'.format(
            num_findings,
            os.path.basename(G.JUNIT_XML_FILENAME)))

    elif num_findings == 1000:
        G.LOGGER.info('Wrote the FIRST {0}(!) findings to the {1} file.'.format(
            num_findings,
            os.path.basename(G.JUNIT_XML_FILENAME)))

    else:
        G.LOGGER.info('Wrote {0} findings to the {1} file.'.format(
            num_findings,
            os.path.basename(G.JUNIT_XML_FILENAME)))

    if G.VERBOSE:
        pass
    # G.LOGGER.info ('Wrote {0}'.format (G.JUNIT_XML_FILENAME))
