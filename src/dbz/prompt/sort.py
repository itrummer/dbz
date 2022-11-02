def sort_rows(table, key_columns):
    """ Sort rows by key columns. 
    
    1. Sort rows by key columns using following comparator:
    - Compare values in key_columns order.
    - <Null> values are sorted last.
    2.<TablePost>

    Args:
        table: <Table>.
        key_columns: list of column indexes.

    Returns:
        <Table> (sorted).
    """