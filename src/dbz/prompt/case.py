def if_else(predicate_column, if_value_column, else_value_column):
    """ Assigns if or else value, based on Boolean value.
    
    1. Replace <Null> values in predicate_column by False.
    2. Assign if or else value, depending on predicate.
    3. Ensure that result is <Column> with values of type <BooleanField>.
    
    Args:
        predicate_column: <Column> containing Booleans.
        if_value_column: Use values from this column (which is <Column>) if predicate is True.
        else_value_column: Use values from this column (which is <Column>) if predicate is False.
    
    Returns:
        <Column> with values of type <BooleanField>.
    """