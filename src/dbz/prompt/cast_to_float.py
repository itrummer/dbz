def cast_to_float(column):
    """ Applies cast to obtain column representing float values.
    
    1. <Null> maps to <Null>.
    2. Other values are casted to <FloatField> values.
    3. Ensure output is <Column> with values of type <FloatField>.
    
    Args:
        column: <Column>.
    
    Returns:
        <Column> with values of type <FloatField>.
    """