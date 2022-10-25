def cast_to_Boolean(column):
    """ Applies cast to obtain column representing Boolean values.
    
    1. <Null> maps to <Null>.
    2. Other values are casted to <BooleanField> values.
    3. Ensure output is <Column> with values of type <BooleanField>.
    
    Args:
        column: <Column>.
    
    Returns:
        <Column> with values of type <BooleanField>.
    """