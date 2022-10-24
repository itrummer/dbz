def fill_int_column(constant, nr_rows):
    """ Returns a column, filled with <IntegerField> values.
    
    1. Create column filled with int values.
    2. Ensure that column type is <IntegerField>.
    
    Args:
        constant: int value or <Null>.
        nr_rows: number of rows in result column.
    
    Returns:
        <Column> with <IntegerField> values.
    """