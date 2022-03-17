import csv


def load_from_csv(path_to_csv):
    """ Load data from .csv file (without header).
    
    Args:
        path_to_csv: path to .csv file to load.
    
    Returns:
        data loaded from .csv file
    """
    with open(path_to_csv, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        data = [row for row in reader]
    return data


def to_columnar_format(csv_data):
    """ Transform data loaded from .csv into columnar representation.
    
    Args:
        csv_data: data loaded using load_from_csv
    
    Returns:
        a list of columns where each column <DataInstructions>.
    """