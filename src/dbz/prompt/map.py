import os


def map_column(column, map_fct):
    """ Applies function to each element of the column.
    
    Args:
        column: a column which <DataInstructions>
        map_fct: apply to each element in column
    
    Returns:
        a column (which <DataInstructions>) with the result of function
    """