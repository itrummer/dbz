def load_from_csv(path_to_csv):
    """ Load data from .csv file (without header).
    
    1. Use pandas (pd) to load .csv file from disk (no header).
    2. Transform into <Table>.
    3. Replace nan values by <Null>.
    4.<TablePost>
    
    Args:
        path_to_csv: path to .csv file to load.
    
    Returns:
        <Table>.
    """