# pylint: disable=C0301			# Line too long
# pylint: disable=C0209                 # Don't require formatted strings.
# 
# Globals are named in CAPITAL letters for easier recognition.
# ======== ========= ========= ========= ========= ========= ========= ==========
from collections import namedtuple

KNOWN_DB = []

MyStruct = namedtuple('MyStruct',
                      '{0} {1} {2} {3} {4} {5} {6}'.format(
                          'database_base',
                          'view_database_base',
                          'change_database_from',
                          'change_database_to',
                          'isa_base_db',
                          'isa_one_to_one_db',
                          'create_svc_view'))

cfg_filename_rel = 'un_re/resources/cfg_known_db.lst'
