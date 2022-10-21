def <binary_op>(column_1, column_2):
    """ True where column_1 <short_op> column_2.
    
    1. Return <Null> for rows where one input row is <Null>.
    2. Return true iff first row <short_op> second row otherwise.
    3. Ensure that the output is <Column>.
    
    Args:
        column_1: <Column>.
        column_2: <Column>.
    
    Returns:
        <Column> containing Boolean values.
    """