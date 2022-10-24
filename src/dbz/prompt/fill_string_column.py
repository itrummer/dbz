def fill_string_column(constant, nr_rows):
    """ Returns a column, filled with <StringField> values.
    
    1. Create column filled with string values.
    2. Ensure that column type is <StringField>.
    
    Args:
        constant: string value or <Null>.
        nr_rows: number of rows in result column.
    
    Returns:
        <Column> with <StringField> values.
    """