def fill_int_column(constant, nr_rows):
    """ Returns <Column>, filled with <IntegerField> values.
    
    1. If constant is not <Null>, round it to integer value.
    2. Create <Column> filled with int values.
    3. Ensure output is <Column> with values of type <IntegerField>.
    
    Args:
        constant: int or float value or <Null>.
        nr_rows: number of rows in result column.
    
    Returns:
        <Column> with <IntegerField> values.
    """