def group_by_<aggregate>(table, agg_column, group_columns):
    """ Calculate <aggregate> for each value combination in group columns.
   
    Args:
        table: <Table>.
        agg_column: index of column for which to calculate <aggregate>.
        group_columns: indexes of columns to group by.
   
    Returns:
        group columns and associated <aggregate>: <Table>.
    """