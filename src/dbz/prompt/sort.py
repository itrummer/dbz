def sort(rows, comparator):
    """ Sort rows using comparator function.
    
    Args:
        rows: a list of rows where each row is a list
        comparator: comparator(i,j) is -1 if row i comes before row j, +1 if row j comes first, 0 if equal
    
    Returns:
        sorted rows
    """