def get_value(column, index):
    """ Returns value in column at given index.
    
    - Transform <BooleanField> into bool.
    - Transform <IntegerField> into int.
    - Transform <FloatField> into float.
    - Transform <StringField> into str.
    
    Args:
        column: <Column>.
        index: item index.
    
    Returns:
        column value at given index.
    """