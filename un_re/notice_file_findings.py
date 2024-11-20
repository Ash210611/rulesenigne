import un_re.global_shared_variables as G


# ======== ========= ========= ========= ========= ========= ========= ==========
def notice_file_findings(input_filename):
    '''
    At the end, will post a success record for files that have no findings
    '''

    for file_obj in G.INPUT_FILES:
        if file_obj.input_filename == input_filename:
            G.INPUT_FILES[file_obj.filenum].num_findings += 1
