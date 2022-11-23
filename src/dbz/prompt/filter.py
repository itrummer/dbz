def filter_table(table, row_idx):
    """ Filter rows in table.
    
    - Replace <Null> values in row_idx by False.
    - Only return table rows where row_idx is True.<TablePost>
    
    Args:
        table: <Table>.
        row_idx: <Column> containing Booleans.
    
    Returns:
        table with rows where row_idx is True.
    """