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


def smart_logical_not(operand):
    """ Negate operand, terating columns and constants separately.
    
    Args:
        operand: either a column or a constant
    
    Returns:
        negated operand
    """
    if is_scalar(operand):
        return not operand
    else:
        return logical_not(operand)
    

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


def adjust_after_project(input_rel, output_rel):
    """ Adjust column height after a projection operation.
    
    Args:
        input_rel: input relation
        output_rel: output relation
    
    Returns:
        output relation with appropriate column height
    """
    out_rows = nr_rows(input_rel[0]) if input_rel else 0
    adjusted = []
    for value in output_rel:
        if is_scalar(value):
            column = fill_column(value, out_rows)
            adjusted += [column]
        else:
            adjusted += [value]
    
    return adjusted


def adjust_after_aggregate(output_rel, grouping):
    """ Adjust column height after an aggregation operation.
    
    Args:
        output_rel: output relation to adjust
        grouping: whether grouping is used
    
    Returns:
        output relation with adjusted column height
    """
    if grouping:
        out_rows = 0
        for value in output_rel:
            if not is_scalar(value):
                cur_rows = nr_rows(value)
                out_rows = max(out_rows, cur_rows)
    else:
        out_rows = 1
    
    adjusted = []
    for value in output_rel:
        if is_scalar(value):
            column = fill_column(value, out_rows)
            adjusted += [column]
        else:
            adjusted += [value]
    
    return adjusted


def complete_outer(in_rows, side, nr_all_cols, inner_rows):
    """ Complete result of inner into result of outer join.
    
    Args:
        in_rows: rows of input relation
        side: 0 if in_rows from left input, 1 otherwise
        nr_all_cols: number of columns in join output
        inner_rows: result of inner join
    
    Returns:
        rows completing result of inner join
    """
    if not in_rows:
        return []
    
    nr_in_cols = len(in_rows[0])
    nr_other_cols = nr_all_cols + nr_in_cols
    matched = set()
    for inner_row in inner_rows:
        start_idx = 0 if side == 0 else nr_other_cols
        ex_end_idx = nr_other_cols if side == 0 else nr_all_cols
        inner_tuple = tuple(inner_row)
        projected = inner_tuple[start_idx:ex_end_idx]
        matched.add(projected)
    
    unmatched = set()
    for in_row in in_rows:
        in_tuple = tuple(in_row)
        if in_tuple not in matched:
            unmatched.add(in_tuple)
    
    nulls = (None,) * nr_other_cols
    if side == 0:
        return [list(it + nulls) for it in unmatched]
    else:
        return [list(nulls + it) for it in unmatched]