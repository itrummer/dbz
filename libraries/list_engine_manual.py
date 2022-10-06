def load_from_csv(path_to_csv):
    """ Load data from .csv file (without header).
    
    Args:
        path_to_csv: path to .csv file to load.
    
    Returns:
        a list of rows where each row is a list
    """
    with open(path_to_csv, 'r') as f:
        data = [row for row in csv.reader(f.read().splitlines())]
    return data





def write_to_csv(table, path_to_csv):
    """ Writes table to a .csv file (without header).
    
    Args:
        table: a list of rows where each row is a list.
        path_to_csv: path to .csv file.
    """
    with open(path_to_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in table:
            writer.writerow(row)





def add_column(table, column):
    """ Add column to table as last column.
   
    Args:
        table: a list of rows where each row is a list.
        column: a list.
   
    Returns:
        table with added column.
    """
    for row in table:
        row.append(column.pop(0))
    return table





def create_table(column_data):
    """ Create table from given columns.
   
    Args:
        column_data: a list of columns where each column is a list.
   
    Returns:
        a list of rows where each row is a list.
    """
    table = []
    for i in range(len(column_data[0])):
        row = []
        for column in column_data:
            row.append(column[i])
        table.append(row)
    return table





def get_column(table, column_idx):
    """ Retrieve one column from table.
   
    Args:
        table: a list of rows where each row is a list.
        column_idx: index of column to extract.
   
    Returns:
        A column which is a list.
    """
    return [row[column_idx] for row in table]





def set_column(table, column_idx, column):
    """ Replace one column in table.
   
    Args:
        table: a list of rows where each row is a list.
        column_idx: index of column to replace.
        column: a list.
   
    Returns:
        Table with replaced column.
    """
    for row in table:
        row[column_idx] = column.pop(0)
    return table



def nr_rows(column):
    """ Returns number of rows in a column.
    
    Args:
        column: a list.
    
    Returns:
        number of elements in column.
    """
    return len(column)



def get_null():
    """ Returns a NULL value: None. (Manually generated) """
    return None


def is_null(column):
    """ Checks if values in a column are None.
    
    Args:
        column: a list.
    
    Returns:
        a list containing Boolean values.
    """
    return [value is None for value in column]





def multiplication(column_1, column_2):
    """ Performs multiplication between two columns.
    
    Args:
        operand_1: a list.
        operand_2: a list.
    
    Returns:
        result column (which is a list), None where any of the operands is None
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
        column: a list.
        index: item index.
    
    Returns:
        column value at given index.
    """
    return column[index]





def fill_column(constant, nr_rows):
    """ Returns a column, filled with constant values.
    
    Args:
        constant: a constant.
        nr_rows: number of rows in result column.
    
    Returns:
        a list.
    """
    return [constant] * nr_rows





def map_column(column, map_fct):
    """ Applies function to each element of the column.
    
    Args:
        column: a list.
        map_fct: apply to each element in column.
    
    Returns:
        a list with the result of function (None if input is None).
    """
    return [map_fct(e) if e is not None else None for e in column]





def cast_to_int(column):
    """ Casts a column to int values.
    
    Args:
        column: a list.
    
    Returns:
        a list with int values.
    """
    return [None if value is None else int(value) for value in column]





def cast_to_float(column):
    """ Casts a column to float values.
    
    Args:
        column: a list.
    
    Returns:
        a list with float values.
    """
    return [None if x is None else float(x) for x in column]





def cast_to_string(column):
    """ Casts a column to string values.
    
    Args:
        column: a list.
    
    Returns:
        a list with string values.
    """
    return [None if item is None else str(item) for item in column]





def is_empty(table):
    """ Check if table is empty.
   
    Args:
        table: a list of rows where each row is a list.
   
    Returns:
        True iff table is empty.
    """
    return len(table) == 0



def sort_rows(table, key_columns):
    """ Sort rows by key columns.
    
    Args:
        table: a list of rows where each row is a list.
        key_columns: list of column indexes.
    
    Returns:
        a list of rows where each row is a list (without index) containing rows sorted by key columns.
    """
    return sorted(table, key=lambda row: [row[i] for i in key_columns])





def first_rows(table, n):
    """ Returns first n rows of table.
   
    Args:
        table: a list of rows where each row is a list.
        n: return at most that many rows.
   
    Returns:
        a list of rows where each row is a list.
    """
    return table[:n]





def substring(column, start, length):
    """ Extracts substring from each column row.
    
    Args:
        column: a list containing strings.
        start: start index of substring (count starts with 1).
        length: length of substring.
    
    Returns:
        a list containing substrings
    """
    return [None if row is None else row[start-1:start-1+length] for row in column]





def addition(column_1, column_2):
    """ Performs addition between two columns.
    
    Args:
        operand_1: a list.
        operand_2: a list.
    
    Returns:
        result column (which is a list), None where any of the operands is None
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
        operand_1: a list.
        operand_2: a list.
    
    Returns:
        result column (which is a list), None where any of the operands is None
    """
    result = []
    for i in range(len(column_1)):
        if column_1[i] is None or column_2[i] is None:
            result.append(None)
        else:
            result.append(column_1[i] - column_2[i])
    return result





def division(column_1, column_2):
    """ Performs division between two columns.
    
    Args:
        operand_1: a list.
        operand_2: a list.
    
    Returns:
        result column (which is a list), None where any of the operands is None
    """
    result = []
    for i in range(len(column_1)):
        if column_1[i] is None or column_2[i] is None:
            result.append(None)
        else:
            result.append(column_1[i] / column_2[i])
    return result





def filter_table(table, row_idx):
    """ Filter rows in table.
    
    Args:
        table: a list of rows where each row is a list.
        row_idx: a list containing Booleans.
    
    Returns:
        table with rows where row_idx is True.
    """
    return [row for row, idx in zip(table, row_idx) if idx]





def less_than(column_1, column_2):
    """ True where operand_1 < operand_2.
    
    Args:
        column_1: a list.
        column_2: a list.
    
    Returns:
        a list containing Boolean values, None where any of the operands is None.
    """
    return [None if (x is None or y is None) else x < y for x, y in zip(column_1, column_2)]





def greater_than(column_1, column_2):
    """ True where operand_1 > operand_2.
    
    Args:
        column_1: a list.
        column_2: a list.
    
    Returns:
        a list containing Boolean values, None where any of the operands is None.
    """
    return [None if (x is None or y is None) else x > y for x, y in zip(column_1, column_2)]





def equal(column_1, column_2):
    """ True where operand_1 = operand_2.
    
    Args:
        column_1: a list.
        column_2: a list.
    
    Returns:
        a list containing Boolean values, None where any of the operands is None.
    """
    return [None if (x is None or y is None) else x == y for x, y in zip(column_1, column_2)]





def not_equal(column_1, column_2):
    """ True where operand_1 <> operand_2.
    
    Args:
        column_1: a list.
        column_2: a list.
    
    Returns:
        a list containing Boolean values, None where any of the operands is None.
    """
    return [None if (x is None or y is None) else x != y for x, y in zip(column_1, column_2)]



def less_than_or_equal(column_1, column_2):
    """ True where operand_1 <= operand_2.
    
    Args:
        column_1: a list.
        column_2: a list.
    
    Returns:
        a list containing Boolean values, None where any of the operands is None.
    """
    return [None if (x is None or y is None) else x <= y for x, y in zip(column_1, column_2)]



def greater_than_or_equal(column_1, column_2):
    """ True where operand_1 >= operand_2.
    
    Args:
        column_1: a list.
        column_2: a list.
    
    Returns:
        a list containing Boolean values, None where any of the operands is None.
    """
    return [None if (x is None or y is None) else x >= y for x, y in zip(column_1, column_2)]





def logical_and(column_1, column_2):
    """ Performs logical and.
    
    Args:
        column_1: a list.
        column_2: a list.
    
    Returns:
        a list containing result of and.
    """
    return [None if column_1[i] is None or column_2[i] is None 
            else column_1[i] and column_2[i] 
            for i in range(len(column_1))]





def logical_or(column_1, column_2):
    """ Performs logical or.
    
    Args:
        column_1: a list.
        column_2: a list.
    
    Returns:
        a list containing result of or.
    """
    return [None if column_1[i] is None or column_2[i] is None 
            else column_1[i] or column_2[i] 
            for i in range(len(column_1))]





def logical_not(column):
    """ Performs logical_not on input column.
    
    Args:
        column: a list with Boolean values.
    
    Returns:
        a list containing result of logical_not.
    """
    return [None if x is None else not x for x in column]





def calculate_sum(column):
    """ Calculate sum of values in column.
    
    Args:
        column: a list.
    
    Returns:
        sum of column values.
    """
    column = [v for v in column if v is not None]
    if not column:
        return None
    sum = 0
    for value in column:
        sum += value
    return sum





def calculate_min(column):
    """ Calculate min of values in column.
    
    Args:
        column: a list.
    
    Returns:
        min of column values.
    """
    column = [v for v in column if v is not None]
    if not column:
        return None
    return min(column)





def calculate_max(column):
    """ Calculate max of values in column.
    
    Args:
        column: a list.
    
    Returns:
        max of column values.
    """
    column = [v for v in column if v is not None]
    if not column:
        return None
    return max(column)





def calculate_avg(column):
    """ Calculate avg of values in column.
    
    Args:
        column: a list.
    
    Returns:
        avg of column values.
    """
    column = [v for v in column if v is not None]
    if not column:
        return None
    return sum(column) / len(column)





def count_distinct(table, column_indexes):
    """ Count distinct value combinations.
   
    Args:
        table: a list of rows where each row is a list.
        column_indexes: count distinct values in those columns.
   
    Returns:
        Number of distinct values.
    """
    distinct_values = set()
    for row in table:
        distinct_values.add(tuple(row[i] for i in column_indexes))
    return len(distinct_values)





def if_else(predicate_column, if_value_column, else_value_column):
    """ Assigns if or else value, based on Boolean value.
    
    Args:
        predicate_column: a list containing Booleans.
        if_value_column: Use values from this column (which is a list) if predicate is True.
        else_value_column: Use values from this column (which is a list) if predicate is False.
    
    Returns:
        a list.
    """
    return [if_value_column[i] if predicate_column[i] else else_value_column[i] for i in range(len(predicate_column))]





def group_by_sum(table, agg_column, group_columns):
    """ Calculate sum for each value combination in group columns.
   
    Args:
        table: a list of rows where each row is a list.
        agg_column: index of column for which to calculate sum.
        group_columns: indexes of columns to group by.
   
    Returns:
        group columns and associated sum: a list of rows where each row is a list.
    """
    # create a dictionary with group columns as keys and sum as values
    group_dict = {}
    for row in table:
        # create a tuple of group columns
        group_tuple = tuple([row[i] for i in group_columns])
        value = row[agg_column]
        # if group_tuple is not in group_dict, add it
        if group_tuple not in group_dict:
            init_val = None if value is None else 0
            group_dict[group_tuple] = init_val
        # add agg_column value to group_dict
        if value is not None:
            group_dict[group_tuple] += value
    # create a list of group columns and associated sum
    group_list = []
    for key in group_dict:
        group_list.append(list(key) + [group_dict[key]])
    return group_list



def group_by_min(table, agg_column, group_columns):
    """ Calculate min for each value combination in group columns.
   
    Args:
        table: a list of rows where each row is a list.
        agg_column: index of column for which to calculate min.
        group_columns: indexes of columns to group by.
   
    Returns:
        group columns and associated min: a list of rows where each row is a list.
    """
    # create a dictionary with group columns as keys and min as values
    group_dict = {}
    for row in table:
        # create a tuple of group columns
        group_tuple = tuple([row[i] for i in group_columns])
        agg_value = row[agg_column]
        # if group_tuple is not in group_dict, add it
        if group_tuple not in group_dict:
            group_dict[group_tuple] = agg_value
        # if agg_column value is less than group_dict value, replace it
        else:
            prior_value = group_dict[group_tuple]
            if prior_value is None:
                group_dict[group_tuple] = agg_value
            elif agg_value is not None:
                group_dict[group_tuple] = min(prior_value, agg_value)
    # create a list of group columns and associated min
    group_list = []
    for key in group_dict:
        group_list.append(list(key) + [group_dict[key]])
    return group_list



def group_by_max(table, agg_column, group_columns):
    """ Calculate max for each value combination in group columns.
   
    Args:
        table: a list of rows where each row is a list.
        agg_column: index of column for which to calculate max.
        group_columns: indexes of columns to group by.
   
    Returns:
        group columns and associated max: a list of rows where each row is a list.
    """
    # create a dictionary with group columns as keys and max as values
    group_dict = {}
    for row in table:
        # create a tuple of group columns
        group_tuple = tuple([row[i] for i in group_columns])
        agg_value = row[agg_column]
        # if group_tuple is not in group_dict, add it
        if group_tuple not in group_dict:
            group_dict[group_tuple] = agg_value
        else:
            prior_value = group_dict[group_tuple]
            if prior_value is None:
                group_dict[group_tuple] = agg_value
            elif agg_value is not None:
                group_dict[group_tuple] = max(prior_value, agg_value)
    # create a list of group columns and associated max
    group_list = []
    for key in group_dict:
        group_list.append(list(key) + [group_dict[key]])
    return group_list



def group_by_avg(table, agg_column, group_columns):
    """ Calculate avg for each value combination in group columns.
   
    Args:
        table: a list of rows where each row is a list.
        agg_column: index of column for which to calculate avg.
        group_columns: indexes of columns to group by.
   
    Returns:
        group columns and associated avg: a list of rows where each row is a list.
    """
    # create a dictionary with group columns as keys and sum as values
    group_dict = {}
    for row in table:
        # create a tuple of group columns
        group_tuple = tuple([row[i] for i in group_columns])
        agg_value = row[agg_column]
        # if group_tuple is not in group_dict, add it
        if group_tuple not in group_dict:
            group_dict[group_tuple] = [0, 0]
        # add agg_column value to group_dict
        group_dict[group_tuple][0] += row[agg_column]
        group_dict[group_tuple][1] += 1
    # create a list of group columns and associated avg
    group_list = []
    for key in group_dict:
        group_list.append(list(key) + [
            None if group_dict[key][1] == 0 else 
            group_dict[key][0] / group_dict[key][1]])
    return group_list



def group_by_count(table, agg_column, group_columns):
    """ Calculate count for each value combination in group columns.
   
    Args:
        table: a list of rows where each row is a list.
        agg_column: index of column for which to calculate count.
        group_columns: indexes of columns to group by.
   
    Returns:
        group columns and associated count: a list of rows where each row is a list.
    """
    # create a dictionary with group columns as keys and count as values
    group_dict = {}
    for row in table:
        # create a tuple of group columns
        group_tuple = tuple([row[i] for i in group_columns])
        # if group_tuple is not in group_dict, add it
        if group_tuple not in group_dict:
            group_dict[group_tuple] = 0
        # add 1 to group_dict
        group_dict[group_tuple] += 1
    # create a list of group columns and associated count
    group_list = []
    for key in group_dict:
        group_list.append(list(key) + [group_dict[key]])
    return group_list



def equality_join(table_1, table_2, key_cols_1, key_cols_2):
    """ Join two tables by equality join.
   
    Args:
        table_1: a list of rows where each row is a list.
        table_2: a list of rows where each row is a list.
        key_cols_1: indexes of join key columns in table 1.
        key_cols_2: indexes of join key columns in table 2.
   
    Returns:
        Joined rows with matching join keys.
    """
    # Create a dictionary of table_1 rows with key_cols_1 as key.
    table_1_dict = {}
    for row in table_1:
        key = tuple([row[i] for i in key_cols_1])
        if key in table_1_dict:
            table_1_dict[key].append(row)
        else:
            table_1_dict[key] = [row]
    del table_1_dict[None]
    # Join table_2 with table_1_dict.
    joined_rows = []
    for row in table_2:
        key = tuple([row[i] for i in key_cols_2])
        if key in table_1_dict:
            for row_1 in table_1_dict[key]:
                joined_rows.append(row_1 + row)
    return joined_rows



def left_outer_join(table_1, table_2, key_cols_1, key_cols_2):
    """ Join two tables by left outer join.
   
    Args:
        table_1: a list of rows where each row is a list.
        table_2: a list of rows where each row is a list.
        key_cols_1: indexes of join key columns in table 1.
        key_cols_2: indexes of join key columns in table 2.
   
    Returns:
        Joined rows with matching join keys.
    """
    # Create a dictionary of table_2 rows with key_cols_2 as key.
    table_2_dict = {}
    for row in table_2:
        key = tuple([row[i] for i in key_cols_2])
        if key in table_2_dict:
            table_2_dict[key].append(row)
        else:
            table_2_dict[key] = [row]
    del table_2_dict[None]
    # Join table_1 with table_2_dict.
    joined_rows = []
    for row in table_1:
        key = tuple([row[i] for i in key_cols_1])
        if key in table_2_dict:
            for row_2 in table_2_dict[key]:
                joined_rows.append(row + row_2)
        else:
            joined_rows.append(row + [None] * len(table_2[0]))
    return joined_rows



def right_outer_join(table_1, table_2, key_cols_1, key_cols_2):
    """ Join two tables by right outer join.
   
    Args:
        table_1: a list of rows where each row is a list.
        table_2: a list of rows where each row is a list.
        key_cols_1: indexes of join key columns in table 1.
        key_cols_2: indexes of join key columns in table 2.
   
    Returns:
        Joined rows with matching join keys.
    """
    # Create a dictionary of table_1 rows with key_cols_1 as key.
    table_1_dict = {}
    for row in table_1:
        key = tuple([row[i] for i in key_cols_1])
        if key in table_1_dict:
            table_1_dict[key].append(row)
        else:
            table_1_dict[key] = [row]
    del table_1_dict[None]
    # Join table_2 with table_1_dict.
    joined_rows = []
    for row in table_2:
        key = tuple([row[i] for i in key_cols_2])
        if key in table_1_dict:
            for row_1 in table_1_dict[key]:
                joined_rows.append(row_1 + row)
        else:
            joined_rows.append([None] * len(key_cols_1) + row)
    return joined_rows



def full_outer_join(table_1, table_2, key_cols_1, key_cols_2):
    """ Join two tables by full outer join.
   
    Args:
        table_1: a list of rows where each row is a list.
        table_2: a list of rows where each row is a list.
        key_cols_1: indexes of join key columns in table 1.
        key_cols_2: indexes of join key columns in table 2.
   
    Returns:
        Joined rows with matching join keys.
    """
    # Create a dictionary of table_1 rows with key_cols_1 as key.
    table_1_dict = {}
    for row in table_1:
        key = tuple([row[i] for i in key_cols_1])
        if key in table_1_dict:
            table_1_dict[key].append(row)
        else:
            table_1_dict[key] = [row]
    # Join table_2 with table_1_dict.
    joined_rows = []
    for row in table_2:
        key = tuple([row[i] for i in key_cols_2])
        if key is not None and key in table_1_dict:
            for row_1 in table_1_dict[key]:
                joined_rows.append(row_1 + row)
        else:
            joined_rows.append(row + [None] * len(table_1[0]))
    # Add rows in table_1 that are not in table_2.
    for key, rows in table_1_dict.items():
        if key is None or key not in [tuple([row[i] for i in key_cols_2]) for row in table_2]:
            for row in rows:
                joined_rows.append(row + [None] * len(table_2[0]))
    return joined_rows

