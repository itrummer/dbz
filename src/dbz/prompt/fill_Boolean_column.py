def fill_Boolean_column(constant, nr_rows):
    """ Returns a column, filled with <BooleanField> values.
    
    1. Create column filled with Boolean values.
    2. Ensure that column type is <BooleanField>.
    
    Args:
        constant: Boolean value or <Null>.
        nr_rows: number of rows in result column.
    
    Returns:
        <Column> with <BooleanField> values.
    """