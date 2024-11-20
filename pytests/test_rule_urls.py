#
# Run this Unit Test from the parent/project directory using this command:
#       python -B -m pytest pytests/test_rule_urls.py
#
# ===============================================================================
# A shell script that would check an URL would look like this:
# export USERNAME=SVP_HIVE_DDL_RE
# export SECRET=NHMbDy3ayj7_6qY3R_Ka	# Has no access to customer data
# 
# TOKEN=`echo -ne "$USERNAME:$PASSWORD" | base64 --wrap 0`
# 
# URL=https://confluence.sys.cigna.com/x/hSirPg
# set -x
# 
# OUT_FILE=Confluence.log
# curl -s -u $USERNAME:$SECRET -L $URL 2>&1 >$OUT_FILE
# RET=$?
# 
# if [ $RET -ne 0 ]; then
#         echo "Error $RET: An error occurred"
# elif [ `grep -c 'Page Not Found' $OUT_FILE` -gt 0 ]; then
#         echo "Page not found."
# fi
# 
# ===============================================================================

import inspect
import os
import re
import subprocess
from pathlib import Path

import pytest

import un_re.global_shared_variables as G
from un_re.authorize_UN_RE import authorize_UN_RE
from un_re.get_rules import get_rules
from un_re.get_rules_urls import get_rules_urls
from un_re.setup_logging import setup_logging


# ===============================================================================
@pytest.fixture
def setup(tmpdir_factory):
    print('Running setup...')

    G.SCRIPT_DIR = str(Path(os.path.dirname(__file__)).parent)

    G.TEMP_DIR = tmpdir_factory.mktemp("logs")
    G.LOG_FILENAME = os.path.join(G.TEMP_DIR, "junk.log")
    setup_logging(G.LOG_FILENAME)

    G.POSTGRES_JSON_FILENAME = os.path.join(G.TEMP_DIR, "postgres.json")
    G.ERROR_FILENAME = os.path.join(G.TEMP_DIR, 'Rules_Engine.errors')
    G.VERBOSE = True

    authorize_UN_RE()

    return 'Setup succeeded'


# ===============================================================================
def test_rules_urls(setup):
    '''
    Check that we can access with every rule url
    '''

    this_function_name = inspect.currentframe().f_code.co_name
    print('')
    print('Running: {0}...'.format(this_function_name))

    rules_with_valid_urls = []  # Don't retrieve the Confluence page again for each RULES_ENGINE_TYPE

    username = os.environ.get('UN_RE_SVP_HIVE_RE_USER')
    password = os.environ.get('UN_RE_SVP_HIVE_RE_PSWD')

    for G.RULES_ENGINE_TYPE in ['DAMODRE', 'ESP_RE', 'HIVE_DDL_RE', 'ORE',
                                'DB2_RE', 'PG_RE', 'DATABRICKS', 'SNOWFLAKE', 'REDSHIFT',
                                'TERADATA_DML', 'TERADATA_DDL']:

        print('-' * 80)
        print(f'Checking URLs for {G.RULES_ENGINE_TYPE} rules')

        get_rules()
        # print (G.AVAILABLE_RULES_TO_CHECK)	# G.AVAILABLE_RULES_TO_CHECK includes g012
        # print (G.SHOULD_CHECK_RULE)	# G.SHOULD_CHECK_RULE includes g012
        # print (G.RULES)		# G.RULES does not include g012

        get_rules_urls()
        # --------------------------------------------------------------
        # Check that rules are loaded
        num = len(G.RULES)
        assert num > 0

        # If the assertion fails,  we will not print the following messages.
        # If the assertion passes, we will     print the following messages.
        print('Good   : All Rules URLs are accessible for {0}, as expected.'.format(
            G.RULES_ENGINE_TYPE))

        # --------------------------------------------------------------
        # Check that all the rules have an URL
        for rule_id in G.SHOULD_CHECK_RULE:
            if G.RULES[rule_id].url is None:
                print(f'Missing URL for Rule {rule_id}: {G.RULES[rule_id].url}')
            assert G.RULES[rule_id].url is not None

        # --------------------------------------------------------------
        # Check that each url is actually available

        if rule_id not in rules_with_valid_urls:

            out_filename = os.path.join(G.TEMP_DIR, "junk.log")

            for rule_id in G.SHOULD_CHECK_RULE:
                url = G.RULES[rule_id].url

                os_command = f'curl -s -u {username}:{password} -L {url} 2>&1 >{out_filename}'

                try:
                    ret = subprocess.call(os_command, shell=True)

                    if ret < 0:
                        G.LOGGER.error(f'Child was terminated by signal {-ret}')
                        sys.exit(E.CURL_ERROR)

                    assert ret == 0

                except OSError as e:
                    G.LOGGER.error(f'Curl execution failed: {e}')
                    sys.exit(E.CURL_ERROR)

                # -----------------------------------------------
                page_not_found = False
                with open(out_filename, 'rt', encoding='utf-8') as out_file:
                    for line in out_file.readlines():
                        if re.search('Page Not Found', line):
                            page_not_found = True

                if page_not_found:
                    print(f'Rule: {rule_id}, URL not accessible.')
                    print(f'URL : {G.RULES[rule_id].url}')
                    assert page_not_found

                # -----------------------------------------------
                found_rule_id = False
                with open(out_filename, 'rt', encoding='utf-8') as out_file:
                    for line in out_file.readlines():
                        if re.search(rule_id, line):
                            found_rule_id = True

                if not found_rule_id:
                    print(f'Rule: {rule_id}, URL contents do not reference the rule ID.')
                    print(f'URL : {G.RULES[rule_id].url}')
                    # Display the file contents too.
                    with open(out_filename, 'rt', encoding='utf-8') as out_file:
                        for line in out_file.readlines():
                            line = line.strip()
                            print(line)
                    assert found_rule_id

                rules_with_valid_urls.append(rule_id)

        # --------------------------------------------------------------
        print('Good   : All Rules for {0} have an URL, as expected.'.format(
            G.RULES_ENGINE_TYPE))

    print('         Passed.')
