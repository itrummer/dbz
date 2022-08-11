'''
Created on Aug 9, 2022

@author: immanueltrummer
'''
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
        do_count = logical_not(logical_or([is_null(op) for op in operands]))
        count_nr = map_column(do_count, lambda d:1 if d else 0)
    else:
        in_card = table_cardinality(table)
        count_nr = fill_column(1, in_card)
    in_cols += [count_nr]
    in_table = create_table(in_cols)
    
    nr_groups = len(groups)
    nr_ops = len(operands)
    in_groups = list(range(nr_groups))
    in_ops = list(range(nr_groups, nr_groups + nr_ops))
    count_nr_idx = len(in_cols)
    
    if distinct:
        grouped_tbl = group_by_sum(in_table, count_nr_idx, in_groups + in_ops)
        dup_cnt = get_column(grouped_tbl, count_nr_idx)
        ones = fill_column(1, nr_rows(dup_cnt))
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
    return map_column(operand, lambda s:s.ljust(pad_to))


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


def smart_substring(src, start, length):
    """ Extracts substrings from columns or scalars.
    
    Args:
        src: extract substrings from this column or scalar
        start: start index of extracted substring
        length: length of extracted substring
    
    Returns:
        extracted substring(s) (column or scalar)
    """
    assert not is_scalar(src), 'Error - cannot extract from scalar source'
    assert is_scalar(start), 'Error - only scalar start indexes supported'
    assert is_scalar(length), 'Error - only scalar length values supported'
    return substring(src, get_value(start, 0), get_value(length, 0))


def ungrouped_count(table, operands, distinct):
    """ Performs count operation without grouping.
    
    Args:
        table: count rows from this table
        operands: indexes of count columns
        distinct: whether distinct keyword is present
    
    Returns:
        a count value
    """
    keep_row = logical_not(logical_or([is_null(op) for op in operands]))
    filtered = filter_table(table, keep_row)
    if distinct:
        return count_distinct(filtered, operands)
    else:
        return table_cardinality(filtered)