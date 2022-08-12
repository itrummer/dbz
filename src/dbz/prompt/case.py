def if_else(predicate_column, if_value_column, else_value_column):
    """ Assigns if or else value, based on Boolean value.
    
    Args:
        predicate_column: <Column> containing Booleans.
        if_value_column: Use values from this column (which is <Column>) if predicate is True.
        else_value_column: Use values from this column (which is <Column>) if predicate is False.
    
    Returns:
        <Column>.
    """