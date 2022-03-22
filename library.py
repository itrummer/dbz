import pandas as pd


def load_from_csv(path_to_csv):
    """ Load data from .csv file (without header).
    
    Args:
        path_to_csv: path to .csv file to load.
    
    Returns:
        data loaded from .csv file
    """
    return pd.read_csv(path_to_csv, header=None)


def to_columnar_format(csv_data):
    """ Transform data loaded from .csv into columnar representation.
    
    Args:
        csv_data: data loaded using load_from_csv
    
    Returns:
        a list of columns where each column is a list.
    """
    return [list(csv_data[i]) for i in range(csv_data.shape[1])]


import pandas as pd


def write_to_csv(rows, path_to_csv):
    """ Writes rows to a .csv file.
    
    Args:
        rows: write these rows into a .csv file
        path_to_csv: path to .csv file
    """
    pd.DataFrame(rows).to_csv(path_to_csv, header=None, index=False)


def to_row_format(columns):
    """ Transforms columnar layout to row-based representation.
    
    Args:
        columns: a list of columns where each column is a list.
    
    Returns:
        a list of rows where each row is a list
    """
    return list(zip(*columns))


def addition(operand_1, operand_2):
    """ Performs addition between two operands.
    
    Args:
        operand_1: a column (which is a list) or a constant
        operand_2: a column (which is a list) or a constant
    
    Returns:
        result of addition (is a list)
    """
    if isinstance(operand_1, list) and isinstance(operand_2, list):
        if len(operand_1) != len(operand_2):
            raise ValueError("Operands must have the same length")
        return [operand_1[i] + operand_2[i] for i in range(len(operand_1))]
    elif isinstance(operand_1, list) and isinstance(operand_2, (int, float)):
        return [operand_1[i] + operand_2 for i in range(len(operand_1))]
    elif isinstance(operand_1, (int, float)) and isinstance(operand_2, list):
        return [operand_1 + operand_2[i] for i in range(len(operand_2))]
    else:
        return operand_1 + operand_2


def subtraction(operand_1, operand_2):
    """ Performs subtraction between two operands.
    
    Args:
        operand_1: a column (which is a list) or a constant
        operand_2: a column (which is a list) or a constant
    
    Returns:
        result of subtraction (is a list)
    """
    if isinstance(operand_1, list) and isinstance(operand_2, list):
        return [operand_1[i] - operand_2[i] for i in range(len(operand_1))]
    elif isinstance(operand_1, list) and not isinstance(operand_2, list):
        return [operand_1[i] - operand_2 for i in range(len(operand_1))]
    elif not isinstance(operand_1, list) and isinstance(operand_2, list):
        return [operand_1 - operand_2[i] for i in range(len(operand_2))]
    else:
        return operand_1 - operand_2


def multiplication(operand_1, operand_2):
    """ Performs multiplication between two operands.
    
    Args:
        operand_1: a column (which is a list) or a constant
        operand_2: a column (which is a list) or a constant
    
    Returns:
        result of multiplication (is a list)
    """
    if isinstance(operand_1, list) and isinstance(operand_2, list):
        if len(operand_1) != len(operand_2):
            raise ValueError("Operands should have the same length")
        return [operand_1[i] * operand_2[i] for i in range(len(operand_1))]
    elif isinstance(operand_1, list) and isinstance(operand_2, (int, float)):
        return [operand_1[i] * operand_2 for i in range(len(operand_1))]
    elif isinstance(operand_1, (int, float)) and isinstance(operand_2, list):
        return [operand_1 * operand_2[i] for i in range(len(operand_2))]
    else:
        return operand_1 * operand_2


def division(operand_1, operand_2):
    """ Performs division between two operands.
    
    Args:
        operand_1: a column (which is a list) or a constant
        operand_2: a column (which is a list) or a constant
    
    Returns:
        result of division (is a list)
    """
    if isinstance(operand_1, list) and isinstance(operand_2, list):
        if len(operand_1) != len(operand_2):
            raise ValueError("Operands should have the same length")
        return [operand_1[i] / operand_2[i] for i in range(len(operand_1))]
    elif isinstance(operand_1, list) and isinstance(operand_2, (int, float)):
        return [operand_1[i] / operand_2 for i in range(len(operand_1))]
    elif isinstance(operand_1, (int, float)) and isinstance(operand_2, list):
        return [operand_1 / operand_2[i] for i in range(len(operand_2))]
    else:
        return operand_1 / operand_2


def normalize(raw_column):
    """ Normalize column representation.
    
    1. Check if raw column is a list.
    2. If not, transform raw column.
    3. The result column is a list.
    """
    if not isinstance(raw_column, list):
        raw_column = [raw_column]
    return raw_column


def calculate_sum(column):
    """ Calculate sum of values in column.
    
    Args:
        column: the column is a list.
    
    Returns:
        sum of column values
    """
    sum_value = 0
    for value in column:
        sum_value += value
    return sum_value


def calculate_min(column):
    """ Calculate min of values in column.
    
    Args:
        column: the column is a list.
    
    Returns:
        min of column values
    """
    return min(column)


def calculate_max(column):
    """ Calculate max of values in column.
    
    Args:
        column: the column is a list.
    
    Returns:
        max of column values
    """
    return max(column)


def calculate_avg(column):
    """ Calculate avg of values in column.
    
    Args:
        column: the column is a list.
    
    Returns:
        avg of column values
    """
    return sum(column) / len(column)


import os


def calculate_row_count(column):
    """ Calculate row count of values in column.
    
    Args:
        column: the column is a list.
    
    Returns:
        row count of column values
    """
    row_count = 0
    for value in column:
        if value != '':
            row_count += 1
    return row_count


import os


def to_tuple_column(rows):
    """ Transform each row into a tuple.
    
    Args:
        rows: a list of rows where each row is a list
    
    Returns:
        one column (which is a list) with tuples
    """
    return [tuple(row) for row in rows]


import os


def rows_to_columns(rows):
    """ Change from row-based to columnar layout.
    
    Args:
        rows: list of rows where each row is a list
    
    Returns:
        a list of columns where each column is a list
    """
    columns = []
    for i in range(len(rows[0])):
        column = []
        for row in rows:
            column.append(row[i])
        columns.append(column)
    return columns


import os


def per_group_sum(agg_column, group_id_column):
    """ Calculate sum for each group.
    
    1. Collect values for each group.
    2. Calculate sum for each group.
    3. Return dictionary mapping each group ID to the sum.
    
    Args:
        agg_column: the column is a list. It contains values to sum.
        group_id_column: the column is a list. It contains for each row the associated group.
    
    Returns:
        a dictionary mapping each group ID to the sum
    """
    # collect values for each group
    group_to_values = {}
    for group_id, value in zip(group_id_column, agg_column):
        if group_id not in group_to_values:
            group_to_values[group_id] = []
        group_to_values[group_id].append(value)
    
    # calculate sum for each group
    group_to_sum = {}
    for group_id, values in group_to_values.items():
        group_to_sum[group_id] = sum(values)
    
    return group_to_sum


import os


def per_group_min(agg_column, group_id_column):
    """ Calculate min for each group.
    
    1. Collect values for each group.
    2. Calculate min for each group.
    3. Return dictionary mapping each group ID to the min.
    
    Args:
        agg_column: the column is a list. It contains values to min.
        group_id_column: the column is a list. It contains for each row the associated group.
    
    Returns:
        a dictionary mapping each group ID to the min
    """
    # 1. Collect values for each group.
    group_to_values = {}
    for group_id, value in zip(group_id_column, agg_column):
        if group_id not in group_to_values:
            group_to_values[group_id] = []
        group_to_values[group_id].append(value)
    
    # 2. Calculate min for each group.
    group_to_min = {}
    for group_id, values in group_to_values.items():
        group_to_min[group_id] = min(values)
    
    return group_to_min


import os


def per_group_max(agg_column, group_id_column):
    """ Calculate max for each group.
    
    1. Collect values for each group.
    2. Calculate max for each group.
    3. Return dictionary mapping each group ID to the max.
    
    Args:
        agg_column: the column is a list. It contains values to max.
        group_id_column: the column is a list. It contains for each row the associated group.
    
    Returns:
        a dictionary mapping each group ID to the max
    """
    # 1. Collect values for each group.
    group_to_values = {}
    for group_id, values in zip(group_id_column, agg_column):
        if group_id not in group_to_values:
            group_to_values[group_id] = []
        group_to_values[group_id].append(values)
    
    # 2. Calculate max for each group.
    group_to_max = {}
    for group_id, values in group_to_values.items():
        group_to_max[group_id] = max(values)
    
    return group_to_max


import os


def per_group_avg(agg_column, group_id_column):
    """ Calculate avg for each group.
    
    1. Collect values for each group.
    2. Calculate avg for each group.
    3. Return dictionary mapping each group ID to the avg.
    
    Args:
        agg_column: the column is a list. It contains values to avg.
        group_id_column: the column is a list. It contains for each row the associated group.
    
    Returns:
        a dictionary mapping each group ID to the avg
    """
    # collect values for each group
    group_to_values = {}
    for group_id, values in zip(group_id_column, agg_column):
        if group_id not in group_to_values:
            group_to_values[group_id] = []
        group_to_values[group_id].append(values)
    
    # calculate avg for each group
    group_to_avg = {}
    for group_id, values in group_to_values.items():
        group_to_avg[group_id] = sum(values) / len(values)
    
    return group_to_avg


import os


def per_group_row_count(column, group_id_column):
    """ Calculate row count for each group.
    
    1. Collect values for each group.
    2. Calculate row count for each group.
    3. Return dictionary mapping each group ID to the row count.
    
    Args:
        column: the column is a list. 
        group_id_column: the column is a list. It contains for each row the associated group.
    
    Returns:
        a dictionary mapping each group ID to the row count
    """
    # Collect values for each group
    group_values = {}
    for i in range(len(column)):
        group_id = group_id_column[i]
        value = column[i]
        if group_id not in group_values:
            group_values[group_id] = []
        group_values[group_id].append(value)
    
    # Calculate row count for each group
    group_row_count = {}
    for group_id in group_values:
        group_row_count[group_id] = len(group_values[group_id])
    
    return group_row_count


def sort(rows, comparator):
    """ Sort rows using comparator function.
    
    Args:
        rows: a list of rows where each row is a list
        comparator: comparator(i,j) is -1 if row i comes before row j, +1 if row j comes first, 0 if equal
    
    Returns:
        sorted rows
    """
    for i in range(len(rows)):
        for j in range(i,len(rows)):
            if comparator(rows[i],rows[j]) == 1:
                rows[i], rows[j] = rows[j], rows[i]
    return rows


def filter_column(column, row_idx):
    """ Filter rows in column.
    
    Args:
        column: the column is a list.
        row_idx: the column is a list, it contains Booleans.
    
    Returns:
        values at positions where row_idx is True.
    """
    return [column[i] for i in range(len(column)) if row_idx[i]]


def less_than(operand_1, operand_2):
    """ True where operand_1 < operand_2.
    
    Args:
        operand_1: either a column (which is a list) or a constant
        operand_2: either a column (which is a list) or a constant
    
    Returns:
        column (which is a list) of Boolean values
    """
    if isinstance(operand_1, list) and isinstance(operand_2, list):
        return [operand_1[i] < operand_2[i] for i in range(len(operand_1))]
    elif isinstance(operand_1, list):
        return [operand_1[i] < operand_2 for i in range(len(operand_1))]
    elif isinstance(operand_2, list):
        return [operand_1 < operand_2[i] for i in range(len(operand_2))]
    else:
        return operand_1 < operand_2


def greater_than(operand_1, operand_2):
    """ True where operand_1 > operand_2.
    
    Args:
        operand_1: either a column (which is a list) or a constant
        operand_2: either a column (which is a list) or a constant
    
    Returns:
        column (which is a list) of Boolean values
    """
    if isinstance(operand_1, list) and isinstance(operand_2, list):
        return [x > y for x, y in zip(operand_1, operand_2)]
    elif isinstance(operand_1, list):
        return [x > operand_2 for x in operand_1]
    elif isinstance(operand_2, list):
        return [operand_1 > y for y in operand_2]
    else:
        return operand_1 > operand_2


def equal(operand_1, operand_2):
    """ True where operand_1 = operand_2.
    
    Args:
        operand_1: either a column (which is a list) or a constant
        operand_2: either a column (which is a list) or a constant
    
    Returns:
        column (which is a list) of Boolean values
    """
    if isinstance(operand_1, list) and isinstance(operand_2, list):
        return [operand_1[i] == operand_2[i] for i in range(len(operand_1))]
    elif isinstance(operand_1, list):
        return [operand_1[i] == operand_2 for i in range(len(operand_1))]
    elif isinstance(operand_2, list):
        return [operand_1 == operand_2[i] for i in range(len(operand_2))]
    else:
        return operand_1 == operand_2


def less_than_or_equal(operand_1, operand_2):
    """ True where operand_1 <= operand_2.
    
    Args:
        operand_1: either a column (which is a list) or a constant
        operand_2: either a column (which is a list) or a constant
    
    Returns:
        column (which is a list) of Boolean values
    """
    if isinstance(operand_1, list) and isinstance(operand_2, list):
        return [operand_1[i] <= operand_2[i] for i in range(len(operand_1))]
    elif isinstance(operand_1, list):
        return [operand_1[i] <= operand_2 for i in range(len(operand_1))]
    elif isinstance(operand_2, list):
        return [operand_1 <= operand_2[i] for i in range(len(operand_2))]
    else:
        return [operand_1 <= operand_2]


def greater_than_or_equal(operand_1, operand_2):
    """ True where operand_1 >= operand_2.
    
    Args:
        operand_1: either a column (which is a list) or a constant
        operand_2: either a column (which is a list) or a constant
    
    Returns:
        column (which is a list) of Boolean values
    """
    if isinstance(operand_1, list) and isinstance(operand_2, list):
        return [operand_1[i] >= operand_2[i] for i in range(len(operand_1))]
    elif isinstance(operand_1, list):
        return [operand_1[i] >= operand_2 for i in range(len(operand_1))]
    elif isinstance(operand_2, list):
        return [operand_1 >= operand_2[i] for i in range(len(operand_2))]
    else:
        return [operand_1 >= operand_2]

