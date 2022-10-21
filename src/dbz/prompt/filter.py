def filter_table(table, row_idx):
    """ Filter rows in table.
    
    1. Replace <Null> values in row_idx by False.
    2. Only return table rows where row_idx is True.
    3.<TablePost>
    
    Args:
        table: <Table>.
        row_idx: <Column> containing Booleans.
    
    Returns:
        table with rows where row_idx is True.
    """