def round_column(column):
    """ Rounds column values.
    
    1. Map <Null> to <Null>.
    2. Round other values.
    
    Args:
        column: <Column>.
    Returns:
        <Column> with rounded values.
    """