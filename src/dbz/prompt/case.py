import os


def if_else(predicate_column, if_value_column, else_value_column):
    """ Assigns if or else value, based on Boolean value.
    
    Args:
        predicate_column: Boolean column (which <DataInstructions>) with predicate evaluation result
        if_value_column: Use values from this column (which <DataInstructions>) if predicate is True
        else_value_column: Use values from this column (which <DataInstructions>) if predicate is False
    
    Returns:
        column (which <DataInstructions>) with if or else values
    """