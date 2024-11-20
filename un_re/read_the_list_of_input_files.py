# pylint: disable=C0209					# Don't require formatted strings.
# pylint: disable=R0911					# Allow more return statements
# pylint: disable=R0912					# Allow more branches

import os
import re
import sys

import un_re.class_definitions as C
import un_re.ERROR_NUMBERS as E
import un_re.global_shared_variables as G

from un_re.check_for_dup_include_files import check_for_dup_include_files
from un_re.dreml_get_list_of_dml_files import dreml_get_list_of_dml_files
from un_re.databricks_get_list_of_input_files import databricks_get_list_of_input_files
from un_re.damodre_get_list_of_input_files import damodre_get_list_of_input_files
from un_re.file_is_utf8_readable import file_is_utf8_readable
from un_re.get_file_contents import get_file_contents
from un_re.indent import indent
from un_re.print_msg import print_msg

from un_re.fprint import fprint
from un_re.should_skip_this_file import should_skip_this_file
from un_re.validate_xml_file import validate_xml_file
from un_re.un_re_get_list_of_excepted_files import un_re_get_list_of_excepted_files


# ===============================================================================
def file_should_be_scanned(full_filename):
    '''
    Check if this file should be scanned.
    Different kinds of files have different acceptance criteria.

    For Hive, the filename must have an extension of .hql, and not be
    found on a list of files to skip.

    Notice that the DATABRICKS Rules Engine type is not in the list below,
    while TERADATA_DML is not.   That is because DATABRICKS may or may not
    use a liquibase.xml file, while the TERADATA_DML never uses a
    liquibase.xml file.
    '''

    # Skip subdirectories, because those are not filenames.
    if os.path.isdir(full_filename):
        return False

    # If the path says do not use, then don't!
    if full_filename.find('do_not_use') > -1:
        return False

    if G.RULES_ENGINE_TYPE == 'HIVE_DDL_RE':

        if re.search(r'\.HQL$', full_filename, re.IGNORECASE):
            return not should_skip_this_file(full_filename)

        return False

    if G.RULES_ENGINE_TYPE in ('TERADATA_DDL', 'DATAOPS_TDV_DDL', 'PG_RE',
                               'DB2_RE', 'REDSHIFT', 'SNOWFLAKE', 'ORE'):

        if re.search(r'\.SQL$', full_filename, re.IGNORECASE):
            return not should_skip_this_file(full_filename)

        return False

    if G.RULES_ENGINE_TYPE == 'DATABRICKS':

        if re.search(r'\.SQL$', full_filename, re.IGNORECASE):
            return not should_skip_this_file(full_filename)
        if re.search(r'\.DDL$', full_filename, re.IGNORECASE):
            return not should_skip_this_file(full_filename)

        print(f'Skipping {full_filename}')
        return False

    if G.RULES_ENGINE_TYPE == 'DATA_MODEL':
        if re.search(r'\.json$', full_filename, re.IGNORECASE):
            return True

        return False

    if G.RULES_ENGINE_TYPE == 'ESP_RE':
        if re.search(r'\.wld$', full_filename, re.IGNORECASE):
            return True

        return False

    # else:
    print_msg('{0}: Unknown RULES_ENGINE_TYPE: {1}'.format(
        os.path.basename(__file__),
        G.RULES_ENGINE_TYPE))
    sys.exit(E.UNKNOWN_RULES_ENGINE_TYPE)


# ===============================================================================
def json_file_should_be_scanned(full_filename):
    """
    Check if this JSON file should be scanned.
        Different kinds of files have different acceptance criteria.
        """

    # Skip subdirectories, because those are not filenames.
    if os.path.isdir(full_filename):
        return False

    # If the path says do not use, then don't!
    if full_filename.find('do_not_use') > -1:
        return False

    if full_filename.find('site-packages') > -1:
        return False  # Skip files on this path.

    if not re.search(r'[0-9]{8}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.json$', full_filename, re.IGNORECASE):
        return False

    return True


# ===============================================================================
def read_the_list_of_input_json_files():
    G.FILE_DICT = {}

    G.LOGGER.info('=' * 80)

    candidate_json_files = []
    for subdir, dirs, files in os.walk(G.INPUT_DIR):
        for this_file in sorted(files):
            candidate_json_file = subdir + os.sep + this_file

            if json_file_should_be_scanned(candidate_json_file):
                candidate_json_files.append(candidate_json_file)

    if len(candidate_json_files) == 0:
        print_msg('Found 0 Erwin JSON files under INPUT_DIR')
        print_msg('')
        sys.exit(E.SUCCESS)

    # Sorting the filename alphabetically should sort them chronologically
    # Select the last one for processing.

    sorted_json_files = sorted(candidate_json_files)

    G.INPUT_FILENAME = sorted_json_files[-1]
    G.INPUT_FILENAME_REL = G.INPUT_FILENAME.replace(G.INPUT_DIR + '/', '')
    G.FILE_DICT[0] = G.INPUT_FILENAME_REL

    if not os.path.isfile(G.INPUT_FILENAME):
        print_msg("ERROR.         This filename is not found.")
        G.LOGGER.error('Tried to find: {0}'.format(G.INPUT_FILENAME))
        G.LOGGER.error('Input_filename_rel: {0}'.format(G.INPUT_FILENAME_REL))
        G.LOGGER.error('')
        sys.exit(E.FILE_NOT_FOUND)

    file_obj = C.InputFile(
        G.INPUT_FILENAME,
        G.INPUT_FILENAME_REL,
        filenum=0)
    file_obj.is_utf8_readable = file_is_utf8_readable(file_obj.input_filename)
    G.INPUT_FILES.append(file_obj)

    G.LOGGER.info('Will scan JSON file: {0} ...\n'.format(
        G.INPUT_FILENAME.replace(G.WORKSPACE, '$WORKSPACE')))

    # Write the list of files to process for analysis
    lst_filename = os.path.join(G.TEMP_DIR, 'files_to_process.lst')
    with open(lst_filename, "w", encoding='utf-8') as lst_file:
        for this_file in G.FILE_DICT:
            fprint(lst_file, this_file)


# ===============================================================================
def INPUT_DIR_read_the_list_of_input_files():
    un_re_get_list_of_excepted_files()

    G.FILE_DICT = {}

    G.LOGGER.info('=' * 80)

    filenum = 0
    num_files_checked = 0
    for subdir, dirs, files in os.walk(G.INPUT_DIR):
        try:
            # Skip dot folders
            for level in subdir.split(r'/'):
                if level[0] == '.':
                    continue
        except:
            pass

        for this_file in sorted(files):
            G.INPUT_FILENAME = os.path.join(subdir, this_file)

            if G.INPUT_FILENAME.find('do_not_use') > -1:
                pass  # Skip files on this path.

            elif G.INPUT_FILENAME.find('site-packages') > -1:
                pass  # Skip files on this path.

            else:
                num_files_checked += 1
                if file_should_be_scanned(G.INPUT_FILENAME):
                    G.INPUT_FILENAME_REL = G.INPUT_FILENAME.replace(G.INPUT_DIR + '/', '')
                    G.FILE_DICT[filenum] = G.INPUT_FILENAME_REL

                    if not os.path.isfile(G.INPUT_FILENAME):
                        print_msg("ERROR.         This filename is not found.")
                        G.LOGGER.error('Tried to find: {0}'.format(G.INPUT_FILENAME))
                        G.LOGGER.error('Input_filename_rel: {0}'.format(G.INPUT_FILENAME_REL))
                        G.LOGGER.error('')
                        sys.exit(E.FILE_NOT_FOUND)

                    file_obj = C.InputFile(
                        G.INPUT_FILENAME,
                        G.INPUT_FILENAME_REL,
                        filenum)

                    file_obj.is_utf8_readable = file_is_utf8_readable(file_obj.input_filename)

                    G.INPUT_FILES.append(file_obj)
                    filenum += 1

    if filenum == 0:
        G.LOGGER.info('Found {0} files to scan under INPUT_DIR'.format(num_files_checked))
        print_msg("Notice: Found no files to scan.")
        sys.exit(E.SUCCESS)
    else:
        if filenum == 1:
            G.LOGGER.info('Found {0} file to process...'.format(filenum))
        else:
            G.LOGGER.info('Found {0} files to process...'.format(filenum))

        if G.VERBOSE:
            # Write the list of files to process for analysis
            lst_filename = os.path.join(G.TEMP_DIR, 'files_to_process.lst')
            with open(lst_filename, "w", encoding='utf-8') as lst_file:
                for this_file in G.FILE_DICT:
                    fprint(lst_file, this_file)


# ======== ========= ========= ========= ========= ========= ========= ==========
def read_the_input_filenames_from_xml_file(xml_filename, check_existence=True):
    '''
    Call this function recursively when a hierarchical XML file is used.
    '''

    input_filenames = []

    xml_content = get_file_contents(xml_filename)

    regex = r"<sqlFile\s+path=.*/>"
    if re.search(regex, xml_content, re.IGNORECASE | re.MULTILINE):
        print_msg("WARNING: Found a reference to a 'sqlFile path'")
        G.LOGGER.warning('Those are deprecated, as they enable bypassing the Rules Engine.')
        G.LOGGER.warning("Please only use 'include file' specifications.")
        G.LOGGER.warning("Views will set runAlways:true, so sqlFile specifications should not be needed.")

    regex = r"(<!--)?.*<include\s+file=.*/>(.*-->)?"
    # Match those whether in comments or not!

    matches = re.finditer(regex, xml_content, re.MULTILINE)

    for matchNum, match in enumerate(matches):

        line = match.group()

        if G.DECOMMENT_XML:
            # Skip XML lines that are commented out.
            # We used to be rely on the XML file being commented
            # out before we got here.  But now that we allow
            # reading hierarchical XML files, there could be any
            # number of other XML files
            if re.search(r'<!--.*?-->', line, re.MULTILINE):
                continue

        # Take the part after the first equals sign
        G.INPUT_FILENAME_REL = line.split('=', 1)[1]

        # # Take the part before the space after that
        # G.INPUT_FILENAME_REL = G.INPUT_FILENAME_REL.split (' ', 1)[0]

        # # Remove the quotes around the relative filename
        # G.INPUT_FILENAME_REL = G.INPUT_FILENAME_REL.strip ('"')

        # Take the part inside the quotes after that.
        G.INPUT_FILENAME_REL = G.INPUT_FILENAME_REL.split('"', 2)[1]

        # Anchor the absolute pth to the XML_DIR.
        G.INPUT_FILENAME = G.XML_DIR + '/' + G.INPUT_FILENAME_REL

        if check_existence and not os.path.exists(G.INPUT_FILENAME):
            G.LOGGER.info('Notice: Failed to find this input filename.')
            indent(f'Failed on matchnum {matchNum}')
            indent('Tried to find {0}'.format(G.INPUT_FILENAME))
            continue

        filename_extension = G.INPUT_FILENAME.split('.')[-1]
        if filename_extension.upper() == 'XML':
            input_filenames += read_the_input_filenames_from_xml_file(G.INPUT_FILENAME)
        # Notice that is recursive.
        else:
            input_filenames.append(G.INPUT_FILENAME_REL)

    return input_filenames


# ======== ========= ========= ========= ========= ========= ========= ==========
def read_the_list_of_input_files_from_xml_file(xml_filename):
    """
    This loop will find the liquibase.xml file, and read the list of
    input files from there that it should process.

    This loop used-to find all '.sql' files starting from the specified
    input directory, and walk all subdirectories.
    """

    # =======================================================================

    G.XML_FILENAME = xml_filename

    G.LOGGER.info('XML_FILENAME = {0}'.format(G.XML_FILENAME.replace(G.WORKSPACE, '$WORKSPACE')))

    if G.RULES_ENGINE_TYPE in ('TERADATA_DDL','DATAOPS_TDV_DDL'):
        validate_xml_file(G.XML_FILENAME)

    G.XML_DIR, G.XML_BASENAME = os.path.split(G.XML_FILENAME)

    G.FILE_DICT = {}

    input_filenames = read_the_input_filenames_from_xml_file(xml_filename)

    # Process the Teradata files in the order they are listed in the XML file
    # Not in sorted alphabetical order

    filenum = 0
    for G.INPUT_FILENAME_REL in input_filenames:

        if not file_should_be_scanned(G.INPUT_FILENAME_REL):
            continue

        G.FILE_DICT[filenum] = G.INPUT_FILENAME_REL
        # Do not save the absolute path of the input filename name in
        # that G_FILE_DICT array yet, because we still need to create a
        # subdirectory for the input file

        G.INPUT_FILENAME = G.XML_DIR + '/' + G.INPUT_FILENAME_REL

        if not os.path.isfile(G.INPUT_FILENAME):
            print_msg("ERROR.         This filename is not found.")
            G.LOGGER.error('Tried to find: {0}'.format(G.INPUT_FILENAME))
            G.LOGGER.error('Input_filename_rel: {0}'.format(G.INPUT_FILENAME_REL))
            G.LOGGER.error('')
            sys.exit(E.FILE_NOT_FOUND)

        file_obj = C.InputFile(
            G.INPUT_FILENAME,
            G.INPUT_FILENAME_REL,
            filenum)

        file_obj.is_utf8_readable = file_is_utf8_readable(file_obj.input_filename)

        G.INPUT_FILES.append(file_obj)
        filenum += 1

    num_file_objs = len(G.INPUT_FILES)
    if num_file_objs == 0:
        print_msg("Notice: Found no files listed in the liquibase.xml file.")
        G.LOGGER.info('XML filename : ' + G.XML_FILENAME)
        sys.exit(0)
    # Exiting 0 as some domains have no DDL files.

    elif num_file_objs == 1:
        indent('Found 1 file to process...')

    else:
        indent(f'Found {num_file_objs} files to process...')


# ======== ========= ========= ========= ========= ========= ========= ==========
def read_the_list_of_input_files():
    '''
    For TERADATA_DDL & 'DATAOPS_TDV_DDL', we must always read the list of DDL files from the
        XML_FILENAME.

    For TERADATA_DML, DAMODRE, DATA_MODEL and ESP_RE, they don't use an
        XML_FILENAME

    For HIVE_DDL_RE, PG_RE, DB2_RE, SNOWFLAKE, DATABRICKS, and REDSHIFT,
        read the list of DDL files from an XML_FILENAME if one was
        specified in the INI file.  Otherwise, without one, do a
        directory scan.
    '''

    if G.RULES_ENGINE_TYPE in ('TERADATA_DDL','DATAOPS_TDV_DDL','DATAOPS_TDV_DDL'):
        read_the_list_of_input_files_from_xml_file(G.XML_FILENAME)
        check_for_dup_include_files()

    elif G.RULES_ENGINE_TYPE == 'TERADATA_DML':

        dreml_get_list_of_dml_files()

    elif G.RULES_ENGINE_TYPE in ('HIVE_DDL_RE',
                                 'PG_RE',
                                 'DB2_RE',
                                 'SNOWFLAKE',
                                 'ORE',
                                 'REDSHIFT'):

        if G.XML_FILENAME is None:
            INPUT_DIR_read_the_list_of_input_files()

        else:
            read_the_list_of_input_files_from_xml_file(G.XML_FILENAME)
            check_for_dup_include_files()

    elif G.RULES_ENGINE_TYPE == 'DATABRICKS':

        if G.XML_FILENAME is None:
            databricks_get_list_of_input_files()
        else:
            read_the_list_of_input_files_from_xml_file(G.XML_FILENAME)
            check_for_dup_include_files()

    elif G.RULES_ENGINE_TYPE == 'DAMODRE':

        damodre_get_list_of_input_files()

    elif G.RULES_ENGINE_TYPE == 'DATA_MODEL':

        read_the_list_of_input_json_files()

    elif G.RULES_ENGINE_TYPE == 'ESP_RE':

        INPUT_DIR_read_the_list_of_input_files()

    else:
        print_msg('{0}: Unknown RULES_ENGINE_TYPE: {1}'.format(
            os.path.basename(__file__),
            G.RULES_ENGINE_TYPE))
        sys.exit(E.UNKNOWN_RULES_ENGINE_TYPE)
