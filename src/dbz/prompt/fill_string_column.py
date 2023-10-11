def fill_string_column(constant, nr_rows):
    """ Returns <Column>, filled with <StringField> values.
    
    1. Create <Column> filled with string values.
    2. Ensure output is <Column> with values of type <StringField>.
    
    Args:
        constant: string value or <Null>.
        nr_rows: number of rows in result column.
    
    Returns:
        <Column> with <StringField> values.
    """