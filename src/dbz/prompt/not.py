def logical_not(column):
    """ Negates input column.
    
    1. Maps <Null> to <Null>.
    2. Negates other values.
    
    Args:
        column: <Column> with values of type <BooleanField>.
    
    Returns:
        <Column> with values of type <BooleanField>.
    """