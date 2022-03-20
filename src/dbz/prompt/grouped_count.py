import os


def per_group_row_count(column, group_id_column):
    """ Calculate row count for each group.
    
    1. Collect values for each group.
    2. Calculate row count for each group.
    3. Return dictionary mapping each group ID to the row count.
    
    Args:
        column: the column <DataInstructions>. 
        group_id_column: the column <DataInstructions>. It contains for each row the associated group.
    
    Returns:
        a dictionary mapping each group ID to the row count
    """