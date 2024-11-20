# Adapted from:
# 	https://runestone.academy/runestone/books/published/pythonds/SortSearch/TheBinarySearch.html
# and
# 	https://stackabuse.com/search-algorithms-in-python/
# ===============================================================================
def binary_search(alist, item):
    first = 0
    last = len(alist) - 1
    index = -1

    while first <= last and (index == -1):
        midpoint = (first + last) // 2
        if alist[midpoint] == item:
            index = midpoint
        else:
            if item < alist[midpoint]:
                last = midpoint - 1
            else:
                first = midpoint + 1

    return index != -1
