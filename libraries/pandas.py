def load_from_csv(path_to_csv):
    """ Load data from .csv file (without header). Rename columns to integer range and drop row index.
    
    Args:
        path_to_csv: path to .csv file to load.
    
    Returns:
        a pandas DataFrame
    """
    data = pd.read_csv(path_to_csv, header=None)
    data.columns = range(data.shape[1])
    data.index = range(data.shape[0])
    return data


def write_to_csv(table, path_to_csv):
    """ Writes table to a .csv file (without header).
    
    Args:
        table: a pandas DataFrame.
        path_to_csv: path to .csv file.
    """
    table.to_csv(path_to_csv, index=False, header=False)
    



def add_column(table, column):
    """ Add column to table as last column.
   
    Args:
        table: a pandas DataFrame.
        column: a pandas series.
   
    Returns:
        table with added column.
    """
    table[column.name] = column
    return table


def create_table(column_data):
    """ Create table from given columns.
   
    Args:
        column_data: a list of columns where each column is a pandas series. Rename columns to integer range and drop row index.
   
    Returns:
        a pandas DataFrame.
    """
    table = pd.concat(column_data, axis=1)
    table.columns = range(len(column_data))
    table.reset_index(drop=True, inplace=True)
    return table


def get_column(table, column_idx):
    """ Retrieve one column from table.
   
    Args:
        table: a pandas DataFrame.
        column_idx: index of column to extract.
   
    Returns:
        A column which is a pandas series.
    """
    return table.iloc[:, column_idx]


def set_column(table, column_idx, column):
    """ Replace one column in table.
   
    Args:
        table: a pandas DataFrame.
        column_idx: index of column to replace.
        column: a pandas series.
   
    Returns:
        Table with replaced column.
    """
    table.iloc[:, column_idx] = column
    return table


def nr_rows(column):
    """ Returns number of rows in a column.
    
    Args:
        column: a pandas series.
    
    Returns:
        number of elements in column.
    """
    return len(column)


def is_null(column):
    """ Checks if values in a column are null.
    
    Args:
        column: a pandas series.
    
    Returns:
        a pandas series containing Boolean values.
    """
    return column.isnull()


def multiplication(column_1, column_2):
    """ Performs multiplication between two columns.
    
    Args:
        operand_1: a pandas series.
        operand_2: a pandas series.
    
    Returns:
        result column (which is a pandas series), NULL where any of the operands is NULL
    """
    return column_1 * column_2


def get_value(column, index):
    """ Returns value in column at given index.
    
    Args:
        column: a pandas series.
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
        a pandas series.
    """
    return pd.Series([constant] * nr_rows)


def map_column(column, map_fct):
    """ Applies function to each element of the column.
    
    Args:
        column: a pandas series.
        map_fct: apply to each element in column.
    
    Returns:
        a pandas series with the result of function (NULL if input is NULL).
    """
    return column.apply(lambda x: map_fct(x) if not pd.isnull(x) else None)


def cast_to_int(column):
    """ Casts a column to int values.
    
    Args:
        column: a pandas series.
    
    Returns:
        a pandas series with int values.
    """
    return column.astype(int)


def cast_to_float(column):
    """ Casts a column to float values.
    
    Args:
        column: a pandas series.
    
    Returns:
        a pandas series with float values.
    """
    return column.astype(float)


def cast_to_string(column):
    """ Casts a column to string values.
    
    Args:
        column: a pandas series.
    
    Returns:
        a pandas series with string values.
    """
    return column.astype(str)


def is_empty(table):
    """ Check if table is empty.
   
    Args:
        table: a pandas DataFrame.
   
    Returns:
        True iff table is empty.
    """
    return table.empty


def sort_rows(table, key_columns):
    """ Sort rows by key columns. Rename columns to integer range and drop row index.
    
    Args:
        table: a pandas DataFrame.
        key_columns: list of column indexes.
    
    Returns:
        a pandas DataFrame (without index) containing rows sorted by key columns.
    """
    # sort by key columns
    table = table.sort_values(key_columns)
    # rename columns to integer range
    table.columns = range(len(table.columns))
    # drop row index
    table = table.reset_index(drop=True)
    return table


def first_rows(table, n):
    """ Returns first n rows of table. Rename columns to integer range and drop row index.
   
    Args:
        table: a pandas DataFrame.
        n: return at most that many rows.
   
    Returns:
        a pandas DataFrame.
    """
    return table.head(n).rename(columns=dict(zip(table.columns, range(len(table.columns))))).reset_index(drop=True)


def substring(column, start, length):
    """ Extracts substring from each column row.
    
    Args:
        column: a pandas series containing strings.
        start: start index of substring (count starts with 1).
        length: length of substring.
    
    Returns:
        a pandas series containing substrings
    """
    return column.str[start-1:start-1+length]


def addition(column_1, column_2):
    """ Performs addition between two columns.
    
    Args:
        operand_1: a pandas series.
        operand_2: a pandas series.
    
    Returns:
        result column (which is a pandas series), NULL where any of the operands is NULL
    """
    return column_1 + column_2


def subtraction(column_1, column_2):
    """ Performs subtraction between two columns.
    
    Args:
        operand_1: a pandas series.
        operand_2: a pandas series.
    
    Returns:
        result column (which is a pandas series), NULL where any of the operands is NULL
    """
    return column_1 - column_2


def division(column_1, column_2):
    """ Performs division between two columns.
    
    Args:
        operand_1: a pandas series.
        operand_2: a pandas series.
    
    Returns:
        result column (which is a pandas series), NULL where any of the operands is NULL
    """
    return column_1 / column_2


def filter_table(table, row_idx):
    """ Filter rows in table. Rename columns to integer range and drop row index.
    
    Args:
        table: a pandas DataFrame.
        row_idx: a pandas series containing Booleans.
    
    Returns:
        table with rows where row_idx is True.
    """
    table = table.loc[row_idx]
    table.columns = range(len(table.columns))
    table.index = range(len(table.index))
    return table


def less_than(column_1, column_2):
    """ True where operand_1 < operand_2.
    
    Args:
        column_1: a pandas series.
        column_2: a pandas series.
    
    Returns:
        a pandas series containing Boolean values, NULL where any of the operands is NULL.
    """
    return column_1 < column_2


def greater_than(column_1, column_2):
    """ True where operand_1 > operand_2.
    
    Args:
        column_1: a pandas series.
        column_2: a pandas series.
    
    Returns:
        a pandas series containing Boolean values, NULL where any of the operands is NULL.
    """
    return column_1 > column_2


def equal(column_1, column_2):
    """ True where operand_1 = operand_2.
    
    Args:
        column_1: a pandas series.
        column_2: a pandas series.
    
    Returns:
        a pandas series containing Boolean values, NULL where any of the operands is NULL.
    """
    return column_1 == column_2


def not_equal(column_1, column_2):
    """ True where operand_1 <> operand_2.
    
    Args:
        column_1: a pandas series.
        column_2: a pandas series.
    
    Returns:
        a pandas series containing Boolean values, NULL where any of the operands is NULL.
    """
    return column_1 != column_2


def less_than_or_equal(column_1, column_2):
    """ True where operand_1 <= operand_2.
    
    Args:
        column_1: a pandas series.
        column_2: a pandas series.
    
    Returns:
        a pandas series containing Boolean values, NULL where any of the operands is NULL.
    """
    return column_1 <= column_2


def greater_than_or_equal(column_1, column_2):
    """ True where operand_1 >= operand_2.
    
    Args:
        column_1: a pandas series.
        column_2: a pandas series.
    
    Returns:
        a pandas series containing Boolean values, NULL where any of the operands is NULL.
    """
    return column_1 >= column_2


def logical_and(column_1, column_2):
    """ Performs logical and.
    
    Args:
        column_1: a pandas series.
        column_2: a pandas series.
    
    Returns:
        a pandas series containing result of and.
    """
    return column_1 & column_2


def logical_or(column_1, column_2):
    """ Performs logical or.
    
    Args:
        column_1: a pandas series.
        column_2: a pandas series.
    
    Returns:
        a pandas series containing result of or.
    """
    return column_1 | column_2


def logical_not(column):
    """ Performs logical_not on input column.
    
    Args:
        column: a pandas series with Boolean values.
    
    Returns:
        a pandas series containing result of logical_not.
    """
    return column.apply(lambda x: not x)


def calculate_sum(column):
    """ Calculate sum of values in column.
    
    Args:
        column: a pandas series.
    
    Returns:
        sum of column values.
    """
    return column.sum()


def calculate_min(column):
    """ Calculate min of values in column.
    
    Args:
        column: a pandas series.
    
    Returns:
        min of column values.
    """
    return column.min()


def calculate_max(column):
    """ Calculate max of values in column.
    
    Args:
        column: a pandas series.
    
    Returns:
        max of column values.
    """
    return column.max()


def calculate_avg(column):
    """ Calculate avg of values in column.
    
    Args:
        column: a pandas series.
    
    Returns:
        avg of column values.
    """
    return column.mean()


def count_distinct(table, column_indexes):
    """ Count distinct value combinations.
   
    Args:
        table: a pandas DataFrame.
        column_indexes: count distinct values in those columns.
   
    Returns:
        Number of distinct values.
    """
    return len(table.drop_duplicates(subset=column_indexes))


def if_else(predicate_column, if_value_column, else_value_column):
    """ Assigns if or else value, based on Boolean value.
    
    Args:
        predicate_column: a pandas series containing Booleans.
        if_value_column: Use values from this column (which is a pandas series) if predicate is True.
        else_value_column: Use values from this column (which is a pandas series) if predicate is False.
    
    Returns:
        a pandas series.
    """
    if_else_column = []
    for i in range(len(predicate_column)):
        if predicate_column[i]:
            if_else_column.append(if_value_column[i])
        else:
            if_else_column.append(else_value_column[i])
    return pd.Series(if_else_column)


def group_by_sum(table, agg_column, group_columns):
    """ Calculate sum for each value combination in group columns. Rename columns to integer range and drop row index.
   
    Args:
        table: a pandas DataFrame.
        agg_column: index of column for which to calculate sum.
        group_columns: indexes of columns to group by.
   
    Returns:
        group columns and associated sum: a pandas DataFrame.
    """
    return table.groupby(group_columns)[agg_column].sum().reset_index()


def group_by_min(table, agg_column, group_columns):
    """ Calculate min for each value combination in group columns. Rename columns to integer range and drop row index.
   
    Args:
        table: a pandas DataFrame.
        agg_column: index of column for which to calculate min.
        group_columns: indexes of columns to group by.
   
    Returns:
        group columns and associated min: a pandas DataFrame.
    """
    return table.groupby(group_columns)[agg_column].min().reset_index()


def group_by_max(table, agg_column, group_columns):
    """ Calculate max for each value combination in group columns. Rename columns to integer range and drop row index.
   
    Args:
        table: a pandas DataFrame.
        agg_column: index of column for which to calculate max.
        group_columns: indexes of columns to group by.
   
    Returns:
        group columns and associated max: a pandas DataFrame.
    """
    return table.groupby(group_columns)[agg_column].max().reset_index()


def group_by_avg(table, agg_column, group_columns):
    """ Calculate avg for each value combination in group columns. Rename columns to integer range and drop row index.
   
    Args:
        table: a pandas DataFrame.
        agg_column: index of column for which to calculate avg.
        group_columns: indexes of columns to group by.
   
    Returns:
        group columns and associated avg: a pandas DataFrame.
    """
    return table.groupby(group_columns)[agg_column].mean().reset_index()


def group_by_count(table, agg_column, group_columns):
    """ Calculate count for each value combination in group columns. Rename columns to integer range and drop row index.
   
    Args:
        table: a pandas DataFrame.
        agg_column: index of column for which to calculate count.
        group_columns: indexes of columns to group by.
   
    Returns:
        group columns and associated count: a pandas DataFrame.
    """
    return table.groupby(group_columns)[agg_column].count().reset_index()


def equality_join(table_1, table_2, key_cols_1, key_cols_2):
    """ Join two tables by equality join. Rename columns to integer range and drop row index.
   
    Args:
        table_1: a pandas DataFrame.
        table_2: a pandas DataFrame.
        key_cols_1: indexes of join key columns in table 1.
        key_cols_2: indexes of join key columns in table 2.
   
    Returns:
        Joined rows with matching join keys.
    """
    # Rename columns to integer range
    table_1.columns = range(table_1.shape[1])
    table_2.columns = range(table_2.shape[1])
    # Join
    table_1['key'] = table_1.iloc[:, key_cols_1].astype(str).sum(axis=1)
    table_2['key'] = table_2.iloc[:, key_cols_2].astype(str).sum(axis=1)
    joined_table = table_1.merge(table_2, how='inner', on='key')
    # Drop row index
    joined_table = joined_table.reset_index(drop=True)
    # Drop key column
    joined_table = joined_table.drop(columns='key')
    return joined_table


def left_outer_join(table_1, table_2, key_cols_1, key_cols_2):
    """ Join two tables by left outer join. Rename columns to integer range and drop row index.
   
    Args:
        table_1: a pandas DataFrame.
        table_2: a pandas DataFrame.
        key_cols_1: indexes of join key columns in table 1.
        key_cols_2: indexes of join key columns in table 2.
   
    Returns:
        Joined rows with matching join keys.
    """
    # Rename columns to integer range
    table_1.columns = range(table_1.shape[1])
    table_2.columns = range(table_2.shape[1])
    # Join
    table_1['key'] = table_1.iloc[:, key_cols_1].astype(str).sum(axis=1)
    table_2['key'] = table_2.iloc[:, key_cols_2].astype(str).sum(axis=1)
    joined_table = table_1.merge(table_2, how='left', on='key')
    # Drop row index
    joined_table = joined_table.reset_index(drop=True)
    # Drop key column
    joined_table = joined_table.drop(columns='key')
    return joined_table


def right_outer_join(table_1, table_2, key_cols_1, key_cols_2):
    """ Join two tables by right outer join. Rename columns to integer range and drop row index.
   
    Args:
        table_1: a pandas DataFrame.
        table_2: a pandas DataFrame.
        key_cols_1: indexes of join key columns in table 1.
        key_cols_2: indexes of join key columns in table 2.
   
    Returns:
        Joined rows with matching join keys.
    """
    # Rename columns to integer range
    table_1.columns = range(table_1.shape[1])
    table_2.columns = range(table_2.shape[1])
    # Join
    table_1['key'] = table_1.iloc[:, key_cols_1].astype(str).sum(axis=1)
    table_2['key'] = table_2.iloc[:, key_cols_2].astype(str).sum(axis=1)
    joined_table = table_1.merge(table_2, how='right', on='key')
    # Drop row index
    joined_table = joined_table.reset_index(drop=True)
    # Drop key column
    joined_table = joined_table.drop(columns='key')
    return joined_table


def full_outer_join(table_1, table_2, key_cols_1, key_cols_2):
    """ Join two tables by full outer join. Rename columns to integer range and drop row index.
   
    Args:
        table_1: a pandas DataFrame.
        table_2: a pandas DataFrame.
        key_cols_1: indexes of join key columns in table 1.
        key_cols_2: indexes of join key columns in table 2.
   
    Returns:
        Joined rows with matching join keys.
    """
    # Rename columns to integer range
    table_1.columns = range(table_1.shape[1])
    table_2.columns = range(table_2.shape[1])
    # Join
    table_1['key'] = table_1.iloc[:, key_cols_1].astype(str).sum(axis=1)
    table_2['key'] = table_2.iloc[:, key_cols_2].astype(str).sum(axis=1)
    joined_table = table_1.merge(table_2, how='outer', on='key')
    # Drop row index
    joined_table = joined_table.reset_index(drop=True)
    # Drop key column
    joined_table = joined_table.drop(columns='key')
    return joined_table

