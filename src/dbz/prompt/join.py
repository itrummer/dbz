def <JoinDefinition>_join(table_1, table_2, key_cols_1, key_cols_2):
    """ Join two tables by <JoinDescription> join.
   
    Args:
        table_1: <Table>.
        table_2: <Table>.
        key_cols_1: indexes of join key columns in table 1.
        key_cols_2: indexes of join key columns in table 2.
   
    Returns:
        Joined rows with matching join keys.
    """