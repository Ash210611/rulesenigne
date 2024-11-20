# pylint: disable=C0209			# Don't require formatted strings

from datetime import datetime
import os
from requests.auth import HTTPBasicAuth
import requests
import urllib3

import un_re.global_shared_variables as G


# ===============================================================================
def load_erwin_json_to_dkc():
    '''
    To avoid coupling with the DKC, handle exceptions if this upload fails.

    In other words, do not fail the Rules Engine if the DKC upload should
    ever fail.
    '''

    if len(G.ERROR_FILENAME) > 0 and \
            os.path.exists(G.ERROR_FILENAME):
        G.LOGGER.info('Will not upload the Erwin JSON file to the DKC since errors were reported.')
        return

    G.LOGGER.info('Uploading the Erwin JSON file to the DKC {0} environment...'.format(
        G.DKC_ENV))

    r = None
    try:
        t1 = datetime.now()

        urls = {'dev': 'https://i-sso.sys.cigna.com',
                'int': 'https://x-sso.sys.cigna.com',
                'prod': 'https://sso.sys.cigna.com'}

        session = requests.Session()

        # Suppress the warning about an invalid SSL certificate
        urllib3.disable_warnings(
            urllib3.exceptions.InsecureRequestWarning)

        # Log into WebSEAL
        auth = HTTPBasicAuth(G.DKC_USERNAME, G.DKC_PASSWORD)
        r = session.get(urls[G.DKC_ENV], auth=auth, verify=False)
        r.raise_for_status()

        # Post file to DKC.
        with open(G.INPUT_FILENAME, 'rb') as dkc_file:
            files = {'file': dkc_file}
            r = session.post(
                urls[G.DKC_ENV] + '/myd_upload/upload/models',
                files=files,
                auth=auth,
                verify=False)

            r.raise_for_status()

        t2 = datetime.now()
        elapsed_time = t2 - t1
        G.LOGGER.info('Done uploading the Erwin JSON file in {0:d} seconds.'.format(
            1 + int(elapsed_time.total_seconds())))

    except requests.exceptions.HTTPError:
        G.LOGGER.error('Failed to upload the Erwin JSON file to the DKC {0} environment.'.format(
            G.DKC_ENV))

        if r is not None:
            G.LOGGER.error(r.text)

    except requests.exceptions.ConnectionError:
        G.LOGGER.error('Connection Error trying to upload the Erwin JSON file to the DKC {0} environment.'.format(
            G.DKC_ENV))

        if r is not None:
            G.LOGGER.error(r)
    except:
        G.LOGGER.error(
            'Unknown exception trying to upload to the DKC {0} environment.'.format(
                G.DKC_ENV))

        # Report what the exception was.
        raise
