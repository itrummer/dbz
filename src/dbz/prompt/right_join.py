def right_outer_join(table_1, table_2, nr_cols_1, key_cols_1, key_cols_2):
    """ Join two tables by right outer join.
    
    1. Index table_1 on key_cols_1.
    2. Iterate over rows from table_2:
      - Check whether index contains key:
        - If yes: add matching row pairs to join result.
        - If no: match with nr_cols_1 <Null> values.
    3. Transform into <Table>.
    4. Return result table.

    Args:
        table_1: <Table>.
        table_2: <Table>.
        nr_cols_1: number of columns in table_1.
        key_cols_1: indexes of join key columns in table 1.
        key_cols_2: indexes of join key columns in table 2.

    Returns:
        Joined rows with matching join keys.
    """