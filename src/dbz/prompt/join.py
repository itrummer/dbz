def <JoinDefinition>_join(table_1, table_2, key_cols_1, key_cols_2):
    """ Join two tables by <JoinDefinition> join. 
    
    1. Index table_1 on key_cols_1.
    2. Index table_2 on key_cols_2.
    3. Join table_1 and table_2 with <JoinDefinition> join.
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