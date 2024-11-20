# pylint:	disable=C0209			# Don't require formatted strings
# pylint:	disable=R0912			# Too many branches
# pylint:	disable=R0915			# Too many statements

import re

import un_re.class_definitions as C
import un_re.global_shared_variables as G
from un_re.count_command_type import count_command_type
from un_re.get_file_contents import get_file_contents
from un_re.indent_warning import indent_warning
from un_re.print_command_summary import print_command_summary
from un_re.rezero_the_command_counters import rezero_the_command_counters
from un_re.split_value_from_line import split_value_from_line


# ===============================================================================
def read_esp_job():
    '''
    Read attributes of the ESP job parsed by Antlr
    '''

    G.ESP_JOB = C.ESPJob(G.INPUT_FILENAME, G.INPUT_FILES)
    num_stmts_in_this_job = 0

    lines = []
    for line in G.ANTLR_LOG_CONTENTS.split('\n'):
        line = line.rstrip()
        lines.append(line)

    # Manually iterate through the list of lines, so I can easily advance
    # to the next line without needing to the push a file pointer.
    line_num = 0
    in_a_job_step = False
    docmember_name = 'None'

    while line_num < len(lines):
        line = lines[line_num]
        if re.search(r'Statement Type               : ', line, re.IGNORECASE):
            num_stmts_in_this_job += 1
            count_command_type('ESP STATEMENT')
            statement_type = split_value_from_line(line)
            if statement_type == 'APPL':
                count_command_type('ESP APPLID')
                line_num += 1
                line = lines[line_num]
                G.ESP_JOB.set_applid(split_value_from_line(line))

            elif statement_type == 'AGENT':
                line_num += 1
                line = lines[line_num]
                if in_a_job_step:
                    G.ESP_STEP.agentname = split_value_from_line(line)
                else:
                    G.ESP_JOB.top_level_agents.append(split_value_from_line(line))

            elif statement_type == 'RESOURCE':
                line_num += 1
                line = lines[line_num]
                resource_name = split_value_from_line(line)
                if in_a_job_step:
                    if re.search(r'THR_AGENT', resource_name, re.IGNORECASE):
                        G.ESP_STEP.resource_agent = resource_name
                    elif re.search(r'THR_.*_MAINT', resource_name, re.IGNORECASE):
                        G.ESP_STEP.resource_buc_code = resource_name
                    else:
                        indent_warning('WARNING: Unknown resource name: {0}'.format(
                            resource_name))
                else:
                    if re.search(r'THR_AGENT', resource_name, re.IGNORECASE):
                        G.ESP_JOB.resource_agents.append(resource_name)
                    elif re.search(r'THR_.*_MAINT', resource_name, re.IGNORECASE):
                        G.ESP_JOB.resource_buc_code = resource_name
                    else:
                        indent_warning('WARNING: Unknown resource name: {0}'.format(
                            resource_name))
            elif statement_type == 'RUN':
                line_num += 1
                line = lines[line_num]
                if in_a_job_step:
                    G.ESP_STEP.frequency = split_value_from_line(line)

            elif statement_type == 'USER':
                line_num += 1
                line = lines[line_num]
                if in_a_job_step:
                    G.ESP_STEP.user = split_value_from_line(line)

            elif statement_type == 'SCRIPTNAME':
                line_num += 1
                line = lines[line_num]
                if in_a_job_step:
                    G.ESP_STEP.scriptname = split_value_from_line(line)

            elif statement_type == 'ARGS':
                line_num += 1
                line = lines[line_num]
                if in_a_job_step:
                    G.ESP_STEP.args = split_value_from_line(line)

            elif statement_type == 'CMDNAME':
                line_num += 1
                line = lines[line_num]
                if in_a_job_step:
                    G.ESP_STEP.cmdname = split_value_from_line(line)

            elif statement_type in ('JOB', 'LINUX_JOB', 'AIX_JOB', 'NT_JOB', 'FILE_TRIGGER'):

                count_command_type('ESP JOB')
                in_a_job_step = True
                G.ESP_STEP = C.ESPStep(statement_type)
                line_num += 1
                line = lines[line_num]
                G.ESP_STEP.job_name = split_value_from_line(line)
                G.ESP_STEP.docmember_name = docmember_name

            elif statement_type == 'INVOKE':

                line_num += 1
                line = split_value_from_line(lines[line_num])
                line = line[1:-1]  # Strip leading and trailing quotes
                line = re.sub(r'\(\$DEFAULT\)', '', line)
                G.ESP_JOB.invoked_library = line

            elif statement_type == 'APPLSTART':
                G.ESP_JOB.found_applstart = True

            elif statement_type == 'APPLEND':
                G.ESP_JOB.found_applend = True

        elif re.search(r'  Docmember name             : ', line, re.IGNORECASE):
            if in_a_job_step:
                G.ESP_STEP.docmember_name = split_value_from_line(line)

        elif re.search(r'  Job Option                 : EXTERNAL', line, re.IGNORECASE):
            if in_a_job_step:
                G.ESP_STEP.is_external = True

        elif re.search(r'Parsed single_statement      : ', line, re.IGNORECASE):
            if in_a_job_step:
                in_a_job_step = False
                G.ESP_JOB.esp_step.append(G.ESP_STEP)
                docmember_name = 'None'

        line_num += 1

    G.ESP_JOB.num_stmts = num_stmts_in_this_job
    G.ESP_JOBS.append(G.ESP_JOB)

    if G.VERBOSE:
        G.LOGGER.debug('ApplID       : {0}'.format(G.ESP_JOB.applid))


# ===============================================================================
def get_esp_antlr_findings_for_1_file(file_num):
    G.FILE_OBJ = G.INPUT_FILES[file_num]

    G.ANTLR_LOG_FILENAME = G.TEMP_DIR + '/' + G.INPUT_FILENAME_REL + '.antlr.re.log'
    # For ESP, there is only 1

    G.ANTLR_LOG_CONTENTS = get_file_contents(G.ANTLR_LOG_FILENAME)

    read_esp_job()


# ===============================================================================
def get_all_esp_antlr_findings():
    '''
    Now that the input files have been parsed, load their findings
    from the Antlr log files into the class objects

    This function will loop through all input filenames, and statements
    from each file, and call the get_antlr_findings function for each one.
    '''

    G.LOGGER.info('Reading results from the Antlr syntax-parsing step...')

    for G.FILE_NUM in range(len(G.FILE_DICT)):
        G.LOGGER.info('=' * 88)
        G.LOGGER.info('File Number  = {0}.'.format(
            G.FILE_NUM + 1))

        if not G.INPUT_FILES[G.FILE_NUM].is_utf8_readable:
            continue

        rezero_the_command_counters()

        G.INPUT_FILENAME_REL = G.FILE_DICT[G.FILE_NUM]

        G.INPUT_FILENAME = G.INPUT_DIR + '/' + G.FILE_DICT[G.FILE_NUM]

        get_esp_antlr_findings_for_1_file(G.FILE_NUM)

        print_command_summary()

    G.LOGGER.info('Done reading results from the Antlr syntax-parsing step.')
    return 0
