# pylint: disable=C0209           # Don't require formtted strings

import un_re.global_shared_variables as G


# ===============================================================================
# -- Universal Bad Character list
def get_bad_char_list():
    G.BAD_CHAR_LIST = []

    G.BAD_CHAR_LIST.append((0x2018, '^', 'left apostrophe CHR(8216)'))
    G.BAD_CHAR_LIST.append((0x2019, '^', 'right apostrophe CHR(8217)'))
    G.BAD_CHAR_LIST.append((0x201c, '^', 'left quote CHR(8220)'))
    G.BAD_CHAR_LIST.append((0x201d, '^', 'right quote CHR(8221)'))
    G.BAD_CHAR_LIST.append((0x2070, '^', 'degree symbol CHR(167)'))
    G.BAD_CHAR_LIST.append((0x22, '^', 'quotes CHR(34)'))
    G.BAD_CHAR_LIST.append((0x25, '^', 'percent symbol CHR(37)'))
    G.BAD_CHAR_LIST.append((0x26, '^', 'ampersand CHR(38)'))
    G.BAD_CHAR_LIST.append((0x263b, '^', 'Non-breaking space CHR(8194)'))
    G.BAD_CHAR_LIST.append((0x27, '^', 'apostrophe CHR(39)'))
    G.BAD_CHAR_LIST.append((0x3f, '^', 'question mark CHR(63)'))
    G.BAD_CHAR_LIST.append((0x5c, '^', 'backslash CHR(92)'))
    G.BAD_CHAR_LIST.append((0x91, '^', 'left apostrophe CHR(145)'))
    G.BAD_CHAR_LIST.append((0x92, '^', 'right apostrophe CHR(146)'))
    G.BAD_CHAR_LIST.append((0x93, '^', 'left quote CHR(147)'))
    G.BAD_CHAR_LIST.append((0x94, '^', 'right quote CHR(148)'))
    G.BAD_CHAR_LIST.append((0xa, '^', 'Line Feed CHR(10)'))
    G.BAD_CHAR_LIST.append((0xa0, '^', 'Non Breaking Space CHR(160)'))
    G.BAD_CHAR_LIST.append((0xa9, '^', 'copyright symbol CHR(0169)'))
    G.BAD_CHAR_LIST.append((0xae, '^', 'trademark symbol CHR(0174)'))
    G.BAD_CHAR_LIST.append((0xb0, '^', 'degree symbol CHR(0176)'))
    G.BAD_CHAR_LIST.append((0xb6, '^', 'Paragraph CHR(0182)'))
    G.BAD_CHAR_LIST.append((0xbc, '^', 'fraction: 1/4 CHR(0188)'))
    G.BAD_CHAR_LIST.append((0xbd, '^', 'fraction: 1/2 CHR(0189)'))
    G.BAD_CHAR_LIST.append((0xbe, '^', 'fraction: 3/4 CHR(0190)'))
    G.BAD_CHAR_LIST.append((0xd, '^', 'CR CHR(013)'))
