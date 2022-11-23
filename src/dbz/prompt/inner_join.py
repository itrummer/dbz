def equality_join(table_1, table_2, key_cols_1, key_cols_2):
    """ Join two tables by inner equality join.
    
    - Index table_2 on key_cols_2.
    - Iterate over rows from table_1:
      - Retrieve matching rows from index.
      - Add row pairs to join result.
    - Transform into <Table>.<TablePost>

    Args:
        table_1: <Table>.
        table_2: <Table>.
        key_cols_1: indexes of join key columns in table 1.
        key_cols_2: indexes of join key columns in table 2.

    Returns:
        <Table>.
    """