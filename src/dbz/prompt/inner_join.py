def <JoinDefinition>_join(table_1, table_2, key_cols_1, key_cols_2):
    """ Join two tables by <JoinDescription> join.
    
    1. Index table_1 on key_cols_1 (do not drop column).
    2. Index table_2 on key_cols_2 (do not drop column).
    3. Join table_1 and table_2:
        -  Use suffix '_1' for columns in table_1.
        -  Use suffix '_2' for columns in table_2.
        -  Use an <JoinDescription> join.
        -  Replace NULL values by <Null>.
    4.<TablePost>

    Args:
        table_1: <Table>.
        table_2: <Table>.
        key_cols_1: indexes of join key columns in table 1.
        key_cols_2: indexes of join key columns in table 2.

    Returns:
        Joined rows with matching join keys.
    """
    def index(