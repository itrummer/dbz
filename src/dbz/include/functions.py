'''
Created on Mar 28, 2022

@author: immanueltrummer
'''
def is_scalar(value):
    """ Returns true iff the value is scalar (i.e., not a column).
    
    Args:
        value: either a scalar value or a column
    
    Returns:
        true iff the value is scalar (not a column)
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return True
    else:
        return False

def expand_to(col_or_const, length):
    """ Expand first operand to column of specified length if required.
    
    Args:
        col_or_const: either a column or a constant
        length: expand to column with this length
    
    Returns:
        the first operand if it is a column or a column containing constant value
    """
    if is_scalar(col_or_const):
        return fill_column(col_or_const, length)
    else:
        return col_or_const

def smart_is_null(operand):
    """ Check whether operand (column or constant) is null.
    
    Args:
        operand: a column or a constant
    
    Returns:
        True wherever operand is null
    """
    if operand is None:
        return True
    elif isinstance(operand, (bool, int, float, str)):
        return False
    else:
        # Reference synthesized code piece
        return is_null(operand)

def smart_logical_and(operands):
    """ Check whether conjunction evaluates to true.
    
    Args:
        operands: a list containing scalar operands or columns
    
    Returns:
        Boolean result (either constant or column)
    """
    cols = []
    has_nulls = False
    for operand in operands:
        if is_scalar(operand):
            if operand is None:
                has_nulls = True
            elif operand == False:
                return False
        else:
            cols += [operand]
    
    if cols:
        if has_nulls:
            raise NotImplementedError('Not implemented: AND with scalar NULL')
        else:
            return logical_and(cols)
    else:
        return None if has_nulls else True

def smart_logical_or(operands):
    """ Check whether disjunction evaluates to true.
    
    Args:
        operands: a list containing scalar operands or columns
    
    Returns:
        a Boolean result (either a Boolean column or a scalar value)
    """
    cols = []
    has_nulls = False
    for operand in operands:
        if is_scalar(operand):
            if operand is None:
                has_nulls = True
            elif operand == True:
                return True
        else:
            cols += [operand]
    
    if cols:
        if has_nulls:
            raise NotImplementedError('Not implemented: OR with scalar NULL')
        else:
            return logical_or(cols)
    else:
        return None if has_nulls else False