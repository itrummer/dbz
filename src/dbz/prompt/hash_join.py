import os


def equi_join(rows_1, rows_2, eq_cols):
    """ Performs equi-join between two input relations.
    
    This join implementation uses hashing on join columns.
    
    Example invocation: 
        join([[1, 2], [3, 4]], [[7, 2]], [(2, 2)])
    Example output:
        [[1, 2, 7, 2]]
    
    Args:
        rows_1: rows of first relation where each row is a list
        rows_2: rows of second relation where each row is a list
        eq_cols: list of pairs representing columns in equality conditions
    
    Returns:
        rows of join result where each row is a list
    """
    result_rows = []