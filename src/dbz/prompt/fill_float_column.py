def fill_float_column(constant, nr_rows):
    """ Returns a column, filled with <FloatField> values.
    
    1. Create column filled with float values.
    2. Ensure that column type is <FloatField>.
    
    Args:
        constant: float value or <Null>.
        nr_rows: number of rows in result column.
    
    Returns:
        <Column> with <FloatField> values.
    """