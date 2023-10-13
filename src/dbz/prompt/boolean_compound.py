def logical_<operator>(column_1, column_2):
    """ Performs logical <operator> (using ternary logic: <Null>, True, and False).
    
    Args:
        column_1: <Column> with values of type <BooleanField> or <Null>.
        column_2: <Column> with values of type <BooleanField> or <Null>.
    
    Returns:
        <Column> with values of type <BooleanField> or <Null>.
    """