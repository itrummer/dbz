'''
Created on Aug 9, 2022

@author: immanueltrummer
'''
def fill_column(constant, cardinality):
    """ Fills column using constant - type detection is a hack! 
    
    Args:
        constant: a constant of type bool, integer, float, or string
        cardinality: number of rows in result column
    
    Returns:
        column of given size, filled with constant
    """
    try:
        return fill_int_column(constant, cardinality)
    except:
        pass
    
    try:
        return fill_float_column(constant, cardinality)
    except:
        pass
    
    return fill_string_column(constant, cardinality)


def multiway_and(operands):
    """ Calculates a logical and between multiple operands.
    
    Args:
        operands: list of Boolean columns
    
    Returns:
        column containing logical and
    """
    max_rows = max([nr_rows(op) for op in operands])
    result = fill_Boolean_column(True, max_rows)
    for op in operands:
        result = logical_and(result, op)
    return result


def multiway_or(operands):
    """ Calculates a logical or between multiple operands.
    
    Args:
        operands: list of Boolean columns
    
    Returns:
        column containing logical or
    """
    max_rows = max([nr_rows(op) for op in operands])
    result = fill_Boolean_column(False, max_rows)
    for op in operands:
        result = logical_or(result, op)
    return result


def grouped_count(table, groups, operands, distinct):
    """ Calculate count with group-by clause.
    
    Args:
        table: count rows of this table
        groups: indexes of group-by columns
        operands: indexes of operand columns
        distinct: whether to count distinct rows only
    
    Returns:
        a column containing the result of aggregation
    """
    in_cols = [get_column(table, g) for g in groups]
    in_cols += [get_column(table, o) for o in operands]
    if operands:
        do_count = logical_not(multiway_or([is_null(op) for op in operands]))
        count_nr = map_column(do_count, lambda d:1 if d else 0)
    else:
        in_card = table_cardinality(table)
        count_nr = fill_int_column(1, in_card)
    in_cols += [count_nr]
    in_table = create_table(in_cols)
    
    nr_groups = len(groups)
    nr_ops = len(operands)
    in_groups = list(range(nr_groups))
    in_ops = list(range(nr_groups, nr_groups + nr_ops))
    count_nr_idx = len(in_cols)-1
    
    if distinct:
        grouped_tbl = group_by_sum(in_table, count_nr_idx, in_groups + in_ops)
        dup_cnt = get_column(grouped_tbl, count_nr_idx)
        ones = fill_int_column(1, nr_rows(dup_cnt))
        no_dup_cnt = min(dup_cnt, ones)
        set_column(grouped_tbl, count_nr_idx, no_dup_cnt)
        return group_by_sum(grouped_tbl, count_nr_idx, in_groups)
    else:
        return group_by_sum(in_table, count_nr_idx, in_groups)


def multiply_by_scalar(column, scalar):
    """ Multiplies column by a scalar.
    
    Args:
        column: a column containing numerical values
        scalar: an integer or float constant
    
    Returns:
        column resulting from multiplication
    """
    scale_to = nr_rows(column)
    const_col = fill_float_column(scalar, scale_to)
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
        cur_size = nr_rows(col)
        if cur_size == max_rows:
            scaled_cols += [col]
        elif cur_size < max_rows and cur_size == 1:
            value = get_value(col, 0)
            scaled_col = fill_column(value, max_rows)
            scaled_cols += [scaled_col]
        else:
            raise ValueError(f'Cannot scale size {cur_size} to {max_rows}')
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


def smart_date_extract(from_date, field):
    """ Extract a property from a date. 
    
    Args:
        from_date: date column or constant (number of days since 1/1/1970)
        field: which field to extract from date (e.g., year)
    
    Returns:
        integer value representing extracted property
    """
    def scalar_extract(from_date, field):
        """ Extracts property from a scalar date (i.e., no column). """
        return getattr(
            datetime.datetime(1970,1,1) +\
            datetime.timedelta(days=from_date), 
            field)
        
    return map_column(from_date, lambda d: scalar_extract(d, field))


def smart_padding(operand, pad_to):
    """ Pad string operands (columns or constants) to given length.
    
    Args:
        operand: either a string column or a string
        pad_to: pad operand to this target length
    
    Returns:
        padded operand
    """
    return map_column(
        operand, lambda s:s.ljust(pad_to) if isinstance(s,str) else s)


def sort_wrapper(table, key_cols, ascending):
    """ Resolves sort direction before calling generated sort function.
    
    Args:
        table: a table to sort
        key_cols: key columns to sort by
        ascending: flag indicating direction for each column
    
    Returns:
        sorted table
    """
    def change_sign(table, key_cols, ascending):
        """ Changes signs of all columns marked as descending.
        
        Args:
            table: change signum for column in this table
            key_cols: key columns for sorting
            ascending: list of flags for each column
        """
        for col_idx, asc in zip(key_cols, ascending):
            if not asc:
                col = get_column(table, col_idx)
                col = multiply_by_scalar(col, -1)
                set_column(table, col_idx, col)
    
    change_sign(table, key_cols, ascending)
    table = sort_rows(table, key_cols)
    change_sign(table, key_cols, ascending)
    return table
    

def table_cardinality(table):
    """ Returns the number of rows in table.
    
    Args:
        table: a table to count rows for
    
    Returns:
        number of rows in table
    """
    if is_empty(table):
        return 0
    else:
        return nr_rows(get_column(table, 0))


def ungrouped_count(table, operands, distinct):
    """ Performs count operation without grouping.
    
    Args:
        table: count rows from this table
        operands: indexes of count columns
        distinct: whether distinct keyword is present
    
    Returns:
        a count value
    """
    if operands:
        op_cols = [get_column(table, op) for op in operands]
        keep_row = logical_not(multiway_or([is_null(col) for col in op_cols]))
        table = filter_table(table, keep_row)
    if distinct:
        return count_distinct(table, operands)
    else:
        return table_cardinality(table)