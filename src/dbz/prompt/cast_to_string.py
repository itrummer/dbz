def cast_to_string(column):
    """ Applies cast to obtain column representing string values.
    
    1. <Null> maps to <Null>.
    2. Other values are casted to <StringField> values.
    3. Ensure output is <Column> with values of type <StringField>.
    
    Args:
        column: <Column>.
    
    Returns:
        <Column> with values of type <StringField>.
    """