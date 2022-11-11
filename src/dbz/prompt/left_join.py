def left_outer_join(table_1, table_2, nr_cols_2, key_cols_1, key_cols_2):
    """ Join two tables by left outer join.
    
    1. Index table_2 on key_cols_2.
    2. Iterate over rows from table_1:
      - Check whether index contains key:
        - If yes: add matching row pairs to join result.
        - If no: match with nr_cols_2 <Null> values.
    3. Transform into <Table>.
    4.<TablePost>

    Args:
        table_1: <Table>.
        table_2: <Table>.
        nr_cols_2: number of columns in table_2.
        key_cols_1: indexes of join key columns in table 1.
        key_cols_2: indexes of join key columns in table 2.

    Returns:
        <Table>.
    """
    def index(