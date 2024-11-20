import os


# ===============================================================================
def find_file(name, path):
    """
    This function will return the first matching filename from the
    starting path.

    Adapted from: https://stackoverflow.com/questions/1724693/find-a-file-in-python
    """

    # for root, dirs, files in os.walk...
    for root, _, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

    # If NO file is found at all, return None.
    return None


# ===============================================================================
def find_all_files(name, path):
    """
    This function will return a list of all matching filenames from the
    starting path.

    Adapted from: https://stackoverflow.com/questions/1724693/find-a-file-in-python
    """

    result = []
    # for root, dirs, files in os.walk(path):
    for root, _, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))

    return result
