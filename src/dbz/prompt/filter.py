def filter_column(column, row_idx):
    """ Filter rows in column.
    
    Args:
        column: the column <DataInstructions>.
        row_idx: the column <DataInstructions>, it contains Booleans.
    
    Returns:
        values at positions where row_idx is True.
    """