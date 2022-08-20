def map_column(column, map_fct):
    """ Applies function to each element of the column.
    
    Args:
        column: <Column>.
        map_fct: apply to each element in column.
    
    Returns:
        <Column> with the result of function (NULL if input is NULL).
    """