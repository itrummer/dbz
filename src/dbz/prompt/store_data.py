import pandas as pd


def write_to_csv(rows, path_to_csv):
    """ Writes rows to a .csv file.
    
    Args:
        rows: write these rows into a .csv file
        path_to_csv: path to .csv file
    """
    pd.DataFrame(rows).to_csv(path_to_csv, header=None, index=False)


def to_row_format(columns):
    """ Transforms columnar layout to row-based representation.
    
    Args:
        columns: a list of columns where each column is a list.
    
    Returns:
        a list of rows where each row is a list
    """