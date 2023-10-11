def fill_float_column(constant, nr_rows):
    """ Returns <Column>, filled with <FloatField> values.
    
    1. Create <Column> filled with float values.
    2. Ensure output is <Column> with values of type <FloatField>.
    
    Args:
        constant: float value or <Null>.
        nr_rows: number of rows in result column.
    
    Returns:
        <Column> with <FloatField> values.
    """