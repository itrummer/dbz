def cast_to_<ToType>(column):
    """ Applies cast to obtain column representing <ToType> values.
    
    1. <Null> maps to <Null>.
    2. Other values are casted to represent <ToType> values.
    3. Ensure output is <Column>.
    
    Args:
        column: <Column>.
    
    Returns:
        <Column>.
    """