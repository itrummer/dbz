def cast_to_int(column):
    """ Applies cast to obtain column representing integer values.
    
    1. <Null> maps to <Null>.
    2. Other values are casted to <IntegerField> values.
    3. Ensure output is <Column> with values of type <IntegerField>.
    
    Args:
        column: <Column>.
    
    Returns:
        <Column> with values of type <IntegerField>.
    """