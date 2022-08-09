def <JoinDefinition>_join(table_1, table_2, table_1_col, table_2_col):
    """ Join two tables by <JoinDescription> join.
   
    Args:
        table_1: a list of rows which are lists.
        table_2: a list of rows which are lists.
        table_1_col: index of column in first table.
        table_2_col: index of column in second table.
   
    Returns:
        Joined table with row combinations where table_1_col equals table_2_col.
    """