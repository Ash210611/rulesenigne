import un_re.global_shared_variables as G

from un_re.fprint import fprint


# ===============================================================================
def add_thread_log_to_main_log() -> None:
    with open(G.LOG_FILENAME, 'a', encoding='utf-8') as log_file:
        with open(G.THREAD_LOG_FILENAME, 'r', encoding='utf-8') as thread_log_file:
            for line in thread_log_file.readlines():
                line = line.rstrip()
                print(line)
                # Use print because it has already been logged.
                fprint(log_file, line)
