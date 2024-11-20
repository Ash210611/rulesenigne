# ======== ========= ========= ========= ========= ========= ========= ==========
import codecs


# ======== ========= ========= ========= ========= ========= ========= ==========
# Taken from the helper.py library of Jeremy Davis.

# ======== ========= ========= ========= ========= ========= ========= ==========
def get_file_contents(filePath):
    """
    This module will read the contents from a named file.

    Example usage:
        file_contents = getFileContent (input_filename)
    """

    with codecs.open(filePath, 'r', encoding='utf-8', errors='ignore') as inFile:
        return inFile.read()
