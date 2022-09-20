def sort_rows(table, key_columns):
    """ Sort rows by key columns.
    
    Args:
        table: <Table>.
        key_columns: list of column indexes.
    
    Returns:
        <Table> (without index) containing rows sorted by key columns.
    """