# File: decomment_xml.py
#
# 
# History
# 10/29/2020 SWC Replaced with a regex, which is more accurate.
# 07/20/2018 SWC Wrote it.

# A possible alternative is described here:
#	https://stackoverflow.com/questions/10436695/python-script-to-remove-all-comments-from-xml-file
# ===============================================================================
# from 	lxml 				import	etree

import re

import un_re.global_shared_variables as G
from un_re.get_file_contents import get_file_contents


# ===============================================================================
def decomment_xml():
    '''
    Write a version of G.XML_FILENAME without comments.
    '''

    xml_file_contents = get_file_contents(G.XML_FILENAME)

    xml_file_contents = re.sub(r'<!--[\s\S]*?-->', '', xml_file_contents)
    # \s matches any whitespace character (equal to [\r\n\t\f\v ])
    # \S matches any non-whitespace character (equal to [^\r\n\t\f\v ])

    nocom_xml_filename = G.XML_FILENAME + '.nocom'

    with open(nocom_xml_filename, "w", encoding='utf-8') as nocom_file:
        nocom_file.write(xml_file_contents)

    return nocom_xml_filename

# ===============================================================================
# def decomment_xml_old ():
# 	nocom_xml_filename = G.XML_FILENAME + '.nocom'
# 
# 	nocom_file = open (nocom_xml_filename, "w")
# 
# 	ch1	= ''	# The ch 1 byte ago
# 	ch2	= ''	# The ch 2 bytes ago
# 	ch3	= ''	# The ch 3 bytes ago
# 
# 	in_xml_comment	= False
# 	with open (G.XML_FILENAME, 'r') as in_file:
# 		for ch in iter(lambda: in_file.read(1), ''):
# 
# 			if 	ch3 == '<' and \
# 				ch2 == '!' and \
# 				ch1 == '-' and \
# 				ch  == '-':
# 				in_xml_comment = True
# 			elif 	ch2 == '-' and \
# 				ch1 == '-' and \
# 				ch  == '>' and \
# 				in_xml_comment:
# 				in_xml_comment = False
# 
# 			if not in_xml_comment:
# 				nocom_file.write (ch)
# 
# 			ch3	= ch2
# 			ch2	= ch1
# 			ch1	= ch
# 
# 	nocom_file.close ()
# 
# 	return nocom_xml_filename
#
