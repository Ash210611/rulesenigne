import os  # for chdir
import sys  # for exit

import requests  # Following sys, for pylint

import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G


# The following urllib3 imports are no longer needed.
# Apparently the certificate issue is fixed, and Veracode objects to
# disabling the certificate warnings.
# from	urllib3				import disable_warnings
# from	urllib3				import exceptions


# ===============================================================================
def antlr_get_jar_file():
    '''
    Handy attributes of the requested object:
        print ('Downloaded  : {0}'.format (my_output_file))
        print ('Content Type: {0}'.format (r.headers['content-type']))
        print ('Encoding    : {0}'.format (r.encoding))
    '''

    download_loc = G.SCRIPT_DIR + '/un_re/Antlr'
    download_filename = f'{download_loc}/{G.ANTLR_JAR_FILENAME}'

    if not os.path.exists(download_filename):

        os.chdir(download_loc)

        url = G.ANTLR_JAR_SOURCE + G.ANTLR_JAR_FILENAME

        r = requests.get(url, verify=G.CERTIFICATE_LOCATION, timeout=60)

        if r.status_code != 200:
            print(f'Failed to download {G.ANTLR_JAR_FILENAME}')
            sys.exit(E.FAILED_TO_DOWNLOAD_FILE)

        my_output_file = G.ANTLR_JAR_FILENAME

        with open(my_output_file, 'wb') as f:
            f.write(r.content)

        if not os.path.exists(download_filename):
            G.LOGGER.error('Error: Failed to find the downloaded jar file.')
            G.LOGGER.error(f'Tried to find: {download_filename}')
            G.LOGGER.error(f'Tried to get that from: {url}')
