import os


def per_group_<aggregate>(agg_column, group_id_column):
    """ Calculate <aggregate> for each group.
    
    1. Collect values for each group.
    2. Calculate <aggregate> for each group.
    3. Return dictionary mapping each group ID to the <aggregate>.
    
    Args:
        agg_column: the column <DataInstructions>. It contains values to <aggregate>.
        group_id_column: the column <DataInstructions>. It contains for each row the associated group.
    
    Returns:
        a dictionary mapping each group ID to the <aggregate>
    """