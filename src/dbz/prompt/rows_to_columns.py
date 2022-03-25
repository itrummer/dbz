import os


def rows_to_columns(rows, nr_columns):
    """ Change from row-based to columnar layout.
    
    Args:
        rows: list of rows where each row is a list
        nr_columns: number of columns in schema
    
    Returns:
        a list of columns where each column <DataInstructions>
    """