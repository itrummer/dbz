'''
Created on Aug 9, 2022

@author: immanueltrummer
'''
def multiply_by_scalar(column, scalar):
    """ Multiplies column by a scalar.
    
    Args:
        column: a column containing numerical values
        scalar: an integer or float constant
    
    Returns:
        column resulting from multiplication
    """
    scale_to = nr_rows(column)
    const_col = fill_column(scalar, scale_to)
    return multiplication(column, const_col)


def scale_columns(columns):
    """ Scale up scalar columns to maximal size.
    
    Args:
        columns: list of columns
    
    Returns:
        list of scaled columns
    """
    max_rows = max([nr_rows(c) for c in columns])
    scaled_cols = []
    for col in columns:
        nr_rows = nr_rows(col)
        if nr_rows == max_rows:
            scaled_cols += [col]
        elif nr_rows < max_rows and nr_rows == 1:
            value = get_value(col, 0)
            scaled_col = fill_column(value, max_rows)
            scaled_cols += [scaled_col]
        else:
            raise ValueError(f'Cannot scale size {nr_rows} to {max_rows}')
    return scaled_cols


def scale_to_table(column, table):
    """ Scales scalar values to table size. 
    
    Args:
        column: column to scale
        table: scale to table cardinality
    
    Returns:
        a scaled column
    """
    first_col = get_column(table, 0)
    tbl_size = nr_rows(first_col)
    col_size = nr_rows(column)
    if col_size == tbl_size:
        return column
    elif col_size == 1:
        value = get_value(column, 0)
        return fill_column(value, tbl_size)
    else:
        raise ValueError('Cannot scale non-scalar column!')


def smart_padding(operand, pad_to):
    """ Pad string operands (columns or constants) to given length.
    
    Args:
        operand: either a string column or a string
        pad_to: pad operand to this target length
    
    Returns:
        padded operand
    """
    return map_column(operand, lambda s:s.ljust(pad_to))