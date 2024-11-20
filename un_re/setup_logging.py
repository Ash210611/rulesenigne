# pylint: disable=C0209			# Don't require formatted strings

import logging
import sys

import un_re.global_shared_variables as G


# ===============================================================================
# Setup the class to copy stdout to the log file.
# Source of this idea:
# https://stackoverflow.com/questions/616645/how-do-i-duplicate-sys-stdout-to-a-log-file-in-python
# ===============================================================================
def setup_logging(log_filename):
    """
    Adapted from Python logging cookbook, found here:
    https://docs.python.org/2/howto/logging-cookbook.html

    See also Connor Finnell's example here:
    http://git.sys.cigna.com/imdevops/pvs-testing-automation/blob/master/Pipeline_IMPVS_INF_Metrics/script.py#L212
    """

    # Specify a format for the loggers to use
    logging_format = logging.Formatter('%(levelname)-8s %(message)s')

    # Create the main logger
    G.LOGGER = logging.getLogger('main')
    G.LOGGER.setLevel(logging.INFO)

    # Setup the console logger
    console_logger = logging.StreamHandler(sys.stdout)
    console_logger.setFormatter(logging_format)
    G.LOGGER.addHandler(console_logger)

    # Setup the logfile logger
    logfile_logger = logging.FileHandler(log_filename, encoding='utf-8')
    logfile_logger.setFormatter(logging_format)
    G.LOGGER.addHandler(logfile_logger)


# ===============================================================================
def setup_thread_logging(log_filename, file_num):
    """
    Thread logging only goes to the log_filename, none to the console output

    This is used during parallel processing, when the threads run in the
    background.  The parent will upload the thread log to the console output
    when the thread is finished.
    """

    # Specify a format for the loggers to use
    logging_format = logging.Formatter('{0:04d}-%(levelname)-8s %(message)s'.format(file_num + 1))

    # Create the main logger
    G.LOGGER = logging.getLogger('thread.{0}'.format(G.FILE_NUM + 1))
    G.LOGGER.setLevel(logging.INFO)

    # Setup the logfile logger
    logfile_logger = logging.FileHandler(log_filename, encoding='utf-8')
    logfile_logger.setFormatter(logging_format)
    G.LOGGER.addHandler(logfile_logger)


# ===============================================================================
def closeup_thread_logging(log_filename):
    logfile_logger = logging.FileHandler(log_filename)
    G.LOGGER.removeHandler(logfile_logger)


# ===============================================================================
def set_verbose_logging():
    # G.LOGGER.info ('Log Level set= {0}'.format (logging.DEBUG))
    G.LOGGER.setLevel(logging.DEBUG)
