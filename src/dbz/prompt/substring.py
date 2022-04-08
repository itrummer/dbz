import os


def substring(column, start, length):
    """ Extracts substring from each column row.
    
    Args:
        column: a column (which <DataInstructions>) of strings
        start: start index of substring (count starts with 1)
        length: length of substring
    
    Returns:
        column (which <DataInstructions>) with substrings
    """