# Import libraries for the following scenario:
# - Uses Pandas dataframes.
# - Uses Pandas dataframes.
import pandas as pd
from abc import ABC, abstractmethod


class Column():
    """ Represents a table column. """
    
    def __init__(self, name, data):
        self.name = name
        self.data = data


class AbstractTable(ABC):
    """ Represents a relational table with data. """
    
    @abstractmethod
    def from_csv(self, csv_path):
        """ Loads table data from csv file. """
        raise NotImplementedError()
    
    @abstractmethod
    def to_csv(self, csv_path):
        """ Writes table data to csv file. """
        raise NotImplementedError()
    
    @abstractmethod
    def add_column(self, column):
        """ Adds given column to table. """
        raise NotImplementedError()
    
    @abstractmethod
    def get_column(self, column_idx):
        """ Returns column with given index. """
        raise NotImplementedError()


class Table(AbstractTable):
    """ Uses Pandas dataframes. """
    
    def __init__(self):
        self.df = pd.DataFrame()
    
    def from_csv(self, csv_path):
        self.df = pd.read_csv(csv_path)
    
    def to_csv(self, csv_path):
        self.df.to_csv(csv_path)
    
    def add_column(self, column):
        self.df[column.name] = column.data
    
    def get_column(self, column_idx):
        return Column(self.df.columns[column_idx], self.df.iloc[:, column_idx])
def GroupedSum(table, agg_cols, group_by_cols):
    """ Calculate aggregate value for each group.
    
    Uses Pandas dataframes.
    
    Args:
        table: calculate aggregate on this table
        agg_cols: column indexes for aggregation
        group_by_cols: group by those columns
    
    Returns:
        new column containing aggregate for each group
    """

    df = table.df
    agg_cols = [df.columns[i] for i in agg_cols]
    group_by_cols = [df.columns[i] for i in group_by_cols]
    df = df.groupby(group_by_cols).agg(sum)[agg_cols]
    return Column(agg_cols[0], df.iloc[:, 0])
def GroupedMin(table, agg_cols, group_by_cols):
    """ Calculate aggregate value for each group.
    
    Uses Pandas dataframes.
    
    Args:
        table: calculate aggregate on this table
        agg_cols: column indexes for aggregation
        group_by_cols: group by those columns
    
    Returns:
        new column containing aggregate for each group
    """

    agg_cols = [table.get_column(col_idx) for col_idx in agg_cols]
    group_by_cols = [table.get_column(col_idx) for col_idx in group_by_cols]
    
    grouped = table.df.groupby(group_by_cols)
    agg_df = grouped.agg({col.name: 'min' for col in agg_cols})
    
    return Column(agg_df.columns[0], agg_df.iloc[:, 0])
def GroupedMax(table, agg_cols, group_by_cols):
    """ Calculate aggregate value for each group.
    
    Uses Pandas dataframes.
    
    Args:
        table: calculate aggregate on this table
        agg_cols: column indexes for aggregation
        group_by_cols: group by those columns
    
    Returns:
        new column containing aggregate for each group
    """

    # Get column names for aggregation.
    agg_col_names = [table.df.columns[i] for i in agg_cols]
    
    # Get column names for group by.
    group_by_col_names = [table.df.columns[i] for i in group_by_cols]
    
    # Calculate aggregate for each group.
    grouped = table.df.groupby(group_by_col_names)
    agg = grouped[agg_col_names].max()
    
    # Add new column to table.
    table.add_column(Column(agg_col_names[0], agg.values))
    
    return table
def GroupedCount(table, agg_cols, group_by_cols):
    """ Calculate aggregate value for each group.
    
    Uses Pandas dataframes.
    
    Args:
        table: calculate aggregate on this table
        agg_cols: column indexes for aggregation
        group_by_cols: group by those columns
    
    Returns:
        new column containing aggregate for each group
    """

    agg_cols = [table.get_column(col_idx) for col_idx in agg_cols]
    group_by_cols = [table.get_column(col_idx) for col_idx in group_by_cols]
    
    # Calculate aggregate for each group.
    grouped = table.df.groupby(group_by_cols)
    agg_values = grouped[agg_cols[0].name].count()
    for agg_col in agg_cols[1:]:
        agg_values = agg_values.combine(grouped[agg_col.name].count(),
                                        lambda x1, x2: x1 + x2)
    
    # Create new column with aggregate values.
    new_col = Column('count', agg_values)
    table.add_column(new_col)
    
    return new_col
def GroupedAvg(table, agg_cols, group_by_cols):
    """ Calculate aggregate value for each group.
    
    Uses Pandas dataframes.
    
    Args:
        table: calculate aggregate on this table
        agg_cols: column indexes for aggregation
        group_by_cols: group by those columns
    
    Returns:
        new column containing aggregate for each group
    """

    # TODO: Implement this function.
    # You can change this function signature according to your needs.
    # You can also split this function into smaller functions.
    # For example, you can split into 3 functions:
    # 1) Grouping rows by group_by_cols
    # 2) Calculating aggregate for each group
    # 3) Adding new column to table
    # You can also split into 2 functions:
    # 1) Grouping rows by group_by_cols
    # 2) Calculating aggregate for each group and adding new column to table
    # You can also split into 4 functions:
    # 1) Grouping rows by group_by_cols
    # 2) Calculating aggregate for each group
    # 3) Adding new column to table
    # 4) Returning new column
    # You can also split into 3 functions:
    # 1) Grouping rows by group_by_cols
    # 2) Calculating aggregate for each group
    # 3) Adding new column to table
    # 4) Returning new column
    # You can also split into 2 functions:
    # 1) Grouping rows by group_by_cols
    # 2) Calculating aggregate for each group
    # 3) Adding new column to table
    # 4) Returning new column
    # You can also split into 1 function:
    # 1) Calculating aggregate for each group
    # 2) Adding new column to table
    # 3) Returning new column
    # You can also split into 1 function:
    # 1) Calculating aggregate for each group
    # 2) Adding new column to table
    # 3) Returning new column
    # You can also split into 1 function:
    # 1) Calculating aggregate for each group
    # 2) Adding new column to table
    # 3) Returning new column
    # You can also split into 1 function:
    # 1) Calculating aggregate for each group
    # 2) Adding new column to table
    # 3) Returning new column
    # You can also split into 1 function:
    # 1) Calculating aggregate for each group
    # 2) Adding new column to table
    # 3) Returning new column
    # You can also split into 1 function:
    # 1) Calculating aggregate for each group
    # 2) Adding new column to table
    # 3) Returning new column
    # You can also split into 1 function:
    # 1) Calculating aggregate for each group
    # 2) Adding new column to table
    # 3) Returning new column
    # You can also split into 1 function:
    # 1) Calculating aggregate for each group
    # 2
def less_than(operand_1, operand_2):
    """ Returns true iff operand_1 < operand_2.
    
    Uses Pandas dataframes.
    
    Args:
        operand_1: a column or a constant
        operand_2: a column or a constant
    
    Returns:
        true iff operand_1 < operand_2
    """

    if isinstance(operand_1, Column) and isinstance(operand_2, Column):
        return operand_1.data < operand_2.data
    elif isinstance(operand_1, Column):
        return operand_1.data < operand_2
    elif isinstance(operand_2, Column):
        return operand_1 < operand_2.data
    else:
        return operand_1 < operand_2
def less_than_or_equal(operand_1, operand_2):
    """ Returns true iff operand_1 <= operand_2.
    
    Uses Pandas dataframes.
    
    Args:
        operand_1: a column or a constant
        operand_2: a column or a constant
    
    Returns:
        true iff operand_1 <= operand_2
    """

    if isinstance(operand_1, Column) and isinstance(operand_2, Column):
        return operand_1.data <= operand_2.data
    elif isinstance(operand_1, Column) and isinstance(operand_2, (int, float)):
        return operand_1.data <= operand_2
    elif isinstance(operand_1, (int, float)) and isinstance(operand_2, Column):
        return operand_1 <= operand_2.data
    else:
        raise ValueError('Invalid operands.')
def equal(operand_1, operand_2):
    """ Returns true iff operand_1 = operand_2.
    
    Uses Pandas dataframes.
    
    Args:
        operand_1: a column or a constant
        operand_2: a column or a constant
    
    Returns:
        true iff operand_1 = operand_2
    """

    if isinstance(operand_1, Column) and isinstance(operand_2, Column):
        return operand_1.data.equals(operand_2.data)
    elif isinstance(operand_1, Column) and isinstance(operand_2, (int, float)):
        return operand_1.data.equals(operand_2)
    elif isinstance(operand_1, (int, float)) and isinstance(operand_2, Column):
        return operand_2.data.equals(operand_1)
    else:
        return operand_1 == operand_2
def greater_than_or_equal(operand_1, operand_2):
    """ Returns true iff operand_1 >= operand_2.
    
    Uses Pandas dataframes.
    
    Args:
        operand_1: a column or a constant
        operand_2: a column or a constant
    
    Returns:
        true iff operand_1 >= operand_2
    """

    if isinstance(operand_1, Column) and isinstance(operand_2, Column):
        return operand_1.data >= operand_2.data
    elif isinstance(operand_1, Column):
        return operand_1.data >= operand_2
    elif isinstance(operand_2, Column):
        return operand_1 >= operand_2.data
    else:
        return operand_1 >= operand_2
def greater_than(operand_1, operand_2):
    """ Returns true iff operand_1 > operand_2.
    
    Uses Pandas dataframes.
    
    Args:
        operand_1: a column or a constant
        operand_2: a column or a constant
    
    Returns:
        true iff operand_1 > operand_2
    """

    if isinstance(operand_1, Column) and isinstance(operand_2, Column):
        return operand_1.data > operand_2.data
    elif isinstance(operand_1, Column):
        return operand_1.data > operand_2
    elif isinstance(operand_2, Column):
        return operand_1 > operand_2.data
    else:
        return operand_1 > operand_2
def addition(operand_1, operand_2):
    """ Performs addition between two operands.
    
    Uses Pandas dataframes.
    
    Args:
        operand_1: a column or a constant
        operand_2: a column or a constant
    
    Returns:
        result of addition
    """

    if isinstance(operand_1, Column) and isinstance(operand_2, Column):
        return operand_1.data + operand_2.data
    elif isinstance(operand_1, Column):
        return operand_1.data + operand_2
    elif isinstance(operand_2, Column):
        return operand_1 + operand_2.data
    else:
        return operand_1 + operand_2
def subtraction(operand_1, operand_2):
    """ Performs subtraction between two operands.
    
    Uses Pandas dataframes.
    
    Args:
        operand_1: a column or a constant
        operand_2: a column or a constant
    
    Returns:
        result of subtraction
    """

    if isinstance(operand_1, Column) and isinstance(operand_2, Column):
        return operand_1.data - operand_2.data
    elif isinstance(operand_1, Column):
        return operand_1.data - operand_2
    elif isinstance(operand_2, Column):
        return operand_1 - operand_2.data
    else:
        return operand_1 - operand_2
def multiplication(operand_1, operand_2):
    """ Performs multiplication between two operands.
    
    Uses Pandas dataframes.
    
    Args:
        operand_1: a column or a constant
        operand_2: a column or a constant
    
    Returns:
        result of multiplication
    """

    if isinstance(operand_1, Column) and isinstance(operand_2, Column):
        return operand_1.data * operand_2.data
    elif isinstance(operand_1, Column) and isinstance(operand_2, (int, float)):
        return operand_1.data * operand_2
    elif isinstance(operand_1, (int, float)) and isinstance(operand_2, Column):
        return operand_1 * operand_2.data
    else:
        raise ValueError('Invalid operands.')
def division(operand_1, operand_2):
    """ Performs division between two operands.
    
    Uses Pandas dataframes.
    
    Args:
        operand_1: a column or a constant
        operand_2: a column or a constant
    
    Returns:
        result of division
    """

    if isinstance(operand_1, Column) and isinstance(operand_2, Column):
        return Table().from_csv('data/division.csv')
    elif isinstance(operand_1, Column):
        return operand_1.data / operand_2
    elif isinstance(operand_2, Column):
        return operand_1 / operand_2.data
    else:
        return operand_1 / operand_2
def pick_rows(table, pick_row):
    """ Creates new table with subset of rows.
    
    Uses Pandas dataframes.
    
    Args:
        table: select rows from this table
        pick_row: column with Boolean flags
    
    Returns:
        rows whose flags are set to True
    """

    return Table()
def top_k(table, sort_cols, ascending, k):
    """ Select top-k rows from table.
    
    Uses Pandas dataframes.
    
    Args:
        table: select rows from this table
        sort_cols: indexes of columns to sort by (list of integers)
        ascending: sort direction for each column (Boolean vector)
        k: select so many rows (-1 for all rows)
    
    Returns:
        new table containing top-k rows in sort order
    """

    df = table.df
    df = df.sort_values(by=df.columns[sort_cols], ascending=ascending)
    if k >= 0:
        df = df.head(k)
    return Table()
new_table = Table()
new_table.from_csv("data/LINEITEM")
result_0 = new_table
last_result = result_0
result_1 = pick_rows(last_result, less_than_or_equal(last_result.get_column(10),10471))
last_result = result_1
result_2 = Table()
column = last_result.get_column(8)
result_2.add_column(column)
column = last_result.get_column(9)
result_2.add_column(column)
column = last_result.get_column(4)
result_2.add_column(column)
column = last_result.get_column(5)
result_2.add_column(column)
column = multiplication(last_result.get_column(5),subtraction(1,last_result.get_column(6)))
result_2.add_column(column)
column = multiplication(multiplication(last_result.get_column(5),subtraction(1,last_result.get_column(6))),addition(1,last_result.get_column(7)))
result_2.add_column(column)
column = last_result.get_column(6)
result_2.add_column(column)
last_result = result_2
result_3 = Table()
result_3.add_column(GroupedSum(table=last_result,agg_cols=[2],group_by_cols=[0, 1]))
result_3.add_column(GroupedSum(table=last_result,agg_cols=[3],group_by_cols=[0, 1]))
result_3.add_column(GroupedSum(table=last_result,agg_cols=[4],group_by_cols=[0, 1]))
result_3.add_column(GroupedSum(table=last_result,agg_cols=[5],group_by_cols=[0, 1]))
result_3.add_column(GroupedAvg(table=last_result,agg_cols=[2],group_by_cols=[0, 1]))
result_3.add_column(GroupedAvg(table=last_result,agg_cols=[3],group_by_cols=[0, 1]))
result_3.add_column(GroupedAvg(table=last_result,agg_cols=[6],group_by_cols=[0, 1]))
result_3.add_column(GroupedCount(table=last_result,agg_cols=[],group_by_cols=[0, 1]))
result_4 = Table()
column = last_result.get_column(0)
result_4.add_column(column)
column = last_result.get_column(1)
result_4.add_column(column)
column = last_result.get_column(2)
result_4.add_column(column)
column = last_result.get_column(3)
result_4.add_column(column)
column = last_result.get_column(4)
result_4.add_column(column)
column = last_result.get_column(5)
result_4.add_column(column)
column = last_result.get_column(6)
result_4.add_column(column)
column = last_result.get_column(7)
result_4.add_column(column)
column = last_result.get_column(8)
result_4.add_column(column)
column = last_result.get_column(9)
result_4.add_column(column)
last_result = result_4
result_5 = top_k(last_result, [0, 1], [True, True], -1)
last_result = result_5
last_result.to_csv("result_1")