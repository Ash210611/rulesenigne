import os

import un_re.global_shared_variables as G
from un_re.indent_error import indent_error
from un_re.indent_info import indent_info


# ======== ========= ========= ========= ========= ========= ========= ==========
def authorize_UN_RE():
    '''
    G.DEV_PASSWORD	= os.environ.get('UN_RE_IMAPPDBA_PSWD', 'UNKNOWN')
    7/1/2022 Apparently DEV_USERNAME and DEV_PASSWORD are not longer needed.

    By default, the DMV_USERNAME will be initialized as global_shared_variables.py
    That default is currently 'rulesengine_adm'.
    But a read-only account should be plenty.
    If the user or their pipeline exports an different username, set
    DMV_USERNAME from that exported value rather than the default.
    '''

    os_dmv_user = os.environ.get('UN_RE_DMV_USER', 'UNKNOWN')
    if os_dmv_user != 'UNKNOWN':
        G.DMV_USERNAME = os_dmv_user

    G.DMV_PASSWORD = os.environ.get('UN_RE_DMV_PSWD', 'UNKNOWN')

    G.DKC_PASSWORD = os.environ.get('UN_RE_DKC_PSWD', 'UNKNOWN')

    if 'UNKNOWN' in (G.DMV_PASSWORD, G.DKC_PASSWORD):
        indent_error('Failed to authorize UN_RE from the environment.')
    else:
        indent_info('Authorized UN_RE from the environment.')
