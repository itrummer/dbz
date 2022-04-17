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


def normalize(raw_column):
    """ Normalize column representation.
    
    1. Check if raw column is a list.
    2. If not, transform raw column.
    3. The result column is a list.
    """
    if not isinstance(raw_column, list):
        raw_column = [raw_column]
    return raw_column


import os


def nr_rows(column):
    """ Returns number of rows in a column (which is a list).
    
    Args:
        column: a column (which is a list)
    
    Returns:
        number of elements in column
    """
    return len(column)


def multiplication(column_1, column_2):
    """ Performs multiplication between two columns.
    
    Args:
        operand_1: a column (which is a list)
        operand_2: a column (which is a list)
    
    Returns:
        result column (which is a list), NULL where any of the operands is NULL
    """
    result = []
    for i in range(len(column_1)):
        if column_1[i] is None or column_2[i] is None:
            result.append(None)
        else:
            result.append(column_1[i] * column_2[i])
    return result


def get_value(column, index):
    """ Returns value in column at given index.
    
    Args:
        column: a column (which is a list)
        index: item index
    
    Returns:
        column value at given index
    """
    return column[index]


import os


def fill_column(constant, nr_rows):
    """ Returns a column (which is a list), filled with constant values.
    
    Args:
        constant: a constant
        nr_rows: number of rows in result column
    
    Returns:
        a column containing constant values where the column is a list
    """
    column = []
    for i in range(nr_rows):
        column.append(constant)
    return column


import os


def map_column(column, map_fct):
    """ Applies function to each element of the column.
    
    Args:
        column: a column which is a list
        map_fct: apply to each element in column
    
    Returns:
        a column (which is a list) with the result of function
    """
    return list(map(map_fct, column))


def addition(column_1, column_2):
    """ Performs addition between two columns.
    
    Args:
        operand_1: a column (which is a list)
        operand_2: a column (which is a list)
    
    Returns:
        result column (which is a list), NULL where any of the operands is NULL
    """
    result = []
    for i in range(len(column_1)):
        if column_1[i] is None or column_2[i] is None:
            result.append(None)
        else:
            result.append(column_1[i] + column_2[i])
    return result


def subtraction(column_1, column_2):
    """ Performs subtraction between two columns.
    
    Args:
        operand_1: a column (which is a list)
        operand_2: a column (which is a list)
    
    Returns:
        result column (which is a list), NULL where any of the operands is NULL
    """
    return [x - y for x, y in zip(column_1, column_2)]


def division(column_1, column_2):
    """ Performs division between two columns.
    
    Args:
        operand_1: a column (which is a list)
        operand_2: a column (which is a list)
    
    Returns:
        result column (which is a list), NULL where any of the operands is NULL
    """
    return [x / y if x is not None and y is not None else None for x, y in zip(column_1, column_2)]


import os


def cast_to_float(column):
    """ Casts a column (which is a list) to float values.
    
    Args:
        column: a column (which is a list)
    
    Returns:
        a column (which is a list) with float values
    """
    for i in range(len(column)):
        column[i] = float(column[i])
    return column


import os


def cast_to_varchar(column):
    """ Casts a column (which is a list) to varchar values.
    
    Args:
        column: a column (which is a list)
    
    Returns:
        a column (which is a list) with varchar values
    """
    for i in range(len(column)):
        column[i] = str(column[i])
    return column


import os


def substring(column, start, length):
    """ Extracts substring from each column row.
    
    Args:
        column: a column (which is a list) of strings
        start: start index of substring (count starts with 1)
        length: length of substring
    
    Returns:
        column (which is a list) with substrings
    """
    for i in range(len(column)):
        column[i] = column[i][start-1:start-1+length]
    return column


def filter_column(column, row_idx):
    """ Filter rows in column.
    
    Args:
        column: the column is a list.
        row_idx: the column is a list, it contains Booleans.
    
    Returns:
        values at positions where row_idx is True.
    """
    return [column[i] for i in range(len(column)) if row_idx[i]]


def less_than(column_1, column_2):
    """ True where operand_1 < operand_2.
    
    Args:
        column_1: a column (which is a list)
        column_2: a column (which is a list)
    
    Returns:
        result column (which is a list) of Boolean values, NULL where any of the operands is NULL
    """
    return [a < b for a, b in zip(column_1, column_2)]


def greater_than(column_1, column_2):
    """ True where operand_1 > operand_2.
    
    Args:
        column_1: a column (which is a list)
        column_2: a column (which is a list)
    
    Returns:
        result column (which is a list) of Boolean values, NULL where any of the operands is NULL
    """
    return [x > y for x, y in zip(column_1, column_2)]


def equal(column_1, column_2):
    """ True where operand_1 = operand_2.
    
    Args:
        column_1: a column (which is a list)
        column_2: a column (which is a list)
    
    Returns:
        result column (which is a list) of Boolean values, NULL where any of the operands is NULL
    """
    return [x == y for x, y in zip(column_1, column_2)]


def not_equal(column_1, column_2):
    """ True where operand_1 <> operand_2.
    
    Args:
        column_1: a column (which is a list)
        column_2: a column (which is a list)
    
    Returns:
        result column (which is a list) of Boolean values, NULL where any of the operands is NULL
    """
    return [not(x == y) for x, y in zip(column_1, column_2)]


def less_than_or_equal(column_1, column_2):
    """ True where operand_1 <= operand_2.
    
    Args:
        column_1: a column (which is a list)
        column_2: a column (which is a list)
    
    Returns:
        result column (which is a list) of Boolean values, NULL where any of the operands is NULL
    """
    return [a <= b for a, b in zip(column_1, column_2)]


def greater_than_or_equal(column_1, column_2):
    """ True where operand_1 >= operand_2.
    
    Args:
        column_1: a column (which is a list)
        column_2: a column (which is a list)
    
    Returns:
        result column (which is a list) of Boolean values, NULL where any of the operands is NULL
    """
    return [a >= b for a, b in zip(column_1, column_2)]


import os


def logical_and(columns):
    """ Performs logical and.
    
    Args:
        columns: list of columns with Boolean values where each column is a list
    
    Returns:
        a column (which is a list) containing result of and
    """
    result = []
    for i in range(len(columns[0])):
        result.append(True)
        for j in range(len(columns)):
            result[i] = result[i] and columns[j][i]
    return result


import os


def logical_or(columns):
    """ Performs logical or.
    
    Args:
        columns: list of columns with Boolean values where each column is a list
    
    Returns:
        a column (which is a list) containing result of or
    """
    result = []
    for i in range(len(columns[0])):
        result.append(any([column[i] for column in columns]))
    return result


import os


def logical_not(column):
    """ Performs logical_not on input column.
    
    Args:
        column: a column (which is a list) with Boolean values
    
    Returns:
        a column (which is a list) containing result of logical_not
    """
    return [not i for i in column]


import os


def rows_to_columns(rows, nr_columns):
    """ Change from row-based to columnar layout.
    
    Args:
        rows: list of rows where each row is a list
        nr_columns: number of columns in schema
    
    Returns:
        a list of columns where each column is a list
    """
    columns = []
    for i in range(nr_columns):
        columns.append([])
    for row in rows:
        for i in range(nr_columns):
            columns[i].append(row[i])
    return columns


import os


def is_null(column):
    """ Checks if values in a column (which is a list) are null.
    
    Args:
        column: a column (which is a list)
    
    Returns:
        Boolean column (which is a list)
    """
    return [x is None for x in column]


def calculate_sum(column):
    """ Calculate sum of values in column.
    
    Args:
        column: the column is a list.
    
    Returns:
        sum of column values
    """
    return sum(column)


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


def if_else(predicate_column, if_value_column, else_value_column):
    """ Assigns if or else value, based on Boolean value.
    
    Args:
        predicate_column: Boolean column (which is a list) with predicate evaluation result
        if_value_column: Use values from this column (which is a list) if predicate is True
        else_value_column: Use values from this column (which is a list) if predicate is False
    
    Returns:
        column (which is a list) with if or else values
    """
    return [if_value_column[i] if predicate_column[i] else else_value_column[i] for i in range(len(predicate_column))]


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
    # collect values for each group
    group_to_values = {}
    for group_id, value in zip(group_id_column, agg_column):
        if group_id not in group_to_values:
            group_to_values[group_id] = []
        group_to_values[group_id].append(value)
    
    # calculate min for each group
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
    # collect values for each group
    group_to_values = {}
    for group_id, value in zip(group_id_column, agg_column):
        if group_id not in group_to_values:
            group_to_values[group_id] = []
        group_to_values[group_id].append(value)
    
    # calculate max for each group
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
    for group_id, value in zip(group_id_column, agg_column):
        if group_id not in group_to_values:
            group_to_values[group_id] = []
        group_to_values[group_id].append(value)
    
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


import os


def equi_join(rows_1, rows_2, eq_cols):
    """ Performs equi-join between two input relations.
    
    This join implementation uses hashing on join columns.
    
    Example invocation: 
        join([[1, 2], [3, 4]], [[7, 2]], [(2, 2)])
    Example output:
        [[1, 2, 7, 2]]
    
    Args:
        rows_1: rows of first relation where each row is a list
        rows_2: rows of second relation where each row is a list
        eq_cols: list of pairs representing columns in equality conditions
    
    Returns:
        rows of join result where each row is a list
    """
    result_rows = []
    hash_table = {}
    for row_2 in rows_2:
        key = tuple([row_2[eq_col[1]] for eq_col in eq_cols])
        if key in hash_table:
            hash_table[key].append(row_2)
        else:
            hash_table[key] = [row_2]
    for row_1 in rows_1:
        key = tuple([row_1[eq_col[0]] for eq_col in eq_cols])
        if key in hash_table:
            for row_2 in hash_table[key]:
                result_rows.append(row_1 + row_2)
    return result_rows


def sort(rows, comparator):
    """ Sort rows using comparator function.
    
    Args:
        rows: a list of rows where each row is a list
        comparator: comparator(i,j) is -1 if row i comes before row j, +1 if row j comes first, 0 if equal
    
    Returns:
        sorted rows
    """
    for i in range(len(rows)):
        for j in range(i+1, len(rows)):
            if comparator(rows[i], rows[j]) > 0:
                rows[i], rows[j] = rows[j], rows[i]
    return rows

