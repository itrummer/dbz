def top_k(table, sort_cols, ascending, k):
    """ Select top-k rows from table.
    
    <OperatorInstructions>
    
    Args:
        table: select rows from this table
        sort_cols: indexes of columns to sort by (list of integers)
        ascending: sort direction for each column (Boolean vector)
        k: select so many rows (-1 for all rows)
    
    Returns:
        new table containing top-k rows in sort order
    """