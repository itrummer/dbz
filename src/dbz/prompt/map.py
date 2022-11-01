def map_column(column, map_fct):
    """ Applies function to each element of the column.
    
    1. Maps <Null> to <Null>.
    2. Use map_fct on other values.
    
    Args:
        column: <Column>.
        map_fct: apply to each element in column.
    
    Returns:
        <Column>.
    """