def substring(column, start, length):
    """ Extracts substring from each column row:
    
    1. Maps <Null> to <Null>.
    2. Maps strings to substrings.
    
    Args:
        column: <Column> containing strings or <Null>.
        start: start index of substring (count starts with 1).
        length: length of substring.
    
    Returns:
        <Column> containing substrings or <Null>.
    """