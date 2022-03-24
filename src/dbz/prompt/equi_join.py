import os


def equi_join(rows_1, rows_2, col_1_idx, col_2_idx):
    """ Performs equi-join between two input relations.
    
    Args:
        rows_1: rows of first relation where each row is a list
        rows_2: rows of second relation where each row is a list
        col_1_idx: index of column in first operand, involved in equality condition
        col_2_idx: index of column in second operand, involved in equality condition
    
    Returns:
        rows of join result where each row is a list
    """
    result_rows = []