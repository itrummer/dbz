def group_by_<aggregate>(table, group_by_col):
    """ Calculate <aggregate> per value in the group-by column.
   
    Args:
        table: <Table>.
        group_by_col: index of column with values to group by.
   
    Returns:
        A table (<Table>) containing two columns: the group ID and the <aggregate>.
    """