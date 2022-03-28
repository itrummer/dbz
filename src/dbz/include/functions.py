'''
Created on Mar 28, 2022

@author: immanueltrummer
'''
def expand_to(col_or_const, length):
    """ Expand first operand to column of specified length if required.
    
    Args:
        col_or_const: either a column or a constant
        length: expand to column with this length
    
    Returns:
        the first operand if it is a column or a column containing constant value
    """
    if isinstance(col_or_const, (bool, int, float, str)):
        return fill_column(col_or_const, length)
    else:
        return col_or_const