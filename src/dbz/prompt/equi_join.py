import os


def equi_join(rows_1, rows_2, eq_col_idxs):
    """ Performs equi-join between two input relations.
    
    Args:
        rows_1: rows of first relation where each row is a list
        rows_2: rows of second relation where each row is a list
        eq_col_idxs: list of index pairs, representing columns in equality conditions
    
    Returns:
        rows of join result where each row is a list
    """
    result_rows = []