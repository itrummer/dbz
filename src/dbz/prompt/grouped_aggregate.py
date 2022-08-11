def group_by_<aggregate>(table, agg_column, group_columns):
    """ Calculate <aggregate> for each group.
   
    Args:
        table: <Table>.
        agg_column: index of column for which to calculate <aggregate>.
        group_by_cols: indexes of columns to group by.
   
    Returns:
        <Table> with group columns and one <aggregate> column.
    """