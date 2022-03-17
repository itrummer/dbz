def per_group_<aggregate>(agg_column, group_id_column):
    """ Calculate <aggregate> for each group.
    
    1. Collect values for each group.
    2. Calculate <aggregate> for each group.
    3. Return one column (each column <DataInstructions>) with <aggregate>s.
    
    Args:
        agg_column: the column <DataInstructions>. It contains values to <aggregate>.
        group_id_column: the column <DataInstructions>. It contains for each row the associated group.
    
    Returns:
        a column (each column <DataInstructions>) with the <aggregate> of each group
    """