from check_datatype_for_classword import check_datatype_for_classword


# ===============================================================================
def check_r306():
    """
    CDs should be a VARCHAR (10)
    Otherwise, they should at least be found on the exception list.
    """

    check_datatype_for_classword('r306', 'CD')
