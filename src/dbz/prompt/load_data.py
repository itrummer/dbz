def load_from_csv(path_to_csv):
    """ Load data from .csv file (without header).
    
    - Use pandas (pd) to load .csv file from disk (no header).
    - Transform into <Table>.
    - Replace nan values by <Null>.<TablePost>
    
    Args:
        path_to_csv: path to .csv file to load.
    
    Returns:
        <Table>.
    """