def write_to_csv(table, path_to_csv):
    """ Writes table to a .csv file (without header).
    
    1. Make necessary transformations, if any.
    2. Use pandas (pd) to_csv method to write to file (no index, no header).
    
    Args:
        table: <Table>.
        path_to_csv: path to .csv file.
    """