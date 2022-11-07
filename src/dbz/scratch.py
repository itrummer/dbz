def check_column_type(*args):
    requirements.add("column_type_test")
    return []
def check_table_type(*args):
    requirements.add("table_type_test")
    return []
def load_from_csv(*args):
    requirements.add("load")
    return []
def write_to_csv(*args):
    requirements.add("store")
    return []
def add_column(*args):
    requirements.add("add_column")
    return []
def create_table(*args):
    requirements.add("create_table")
    return []
def get_column(*args):
    requirements.add("get_column")
    return []
def set_column(*args):
    requirements.add("set_column")
    return []
def nr_rows(*args):
    requirements.add("nr_rows")
    return []
def is_null(*args):
    requirements.add("is_null")
    return []
def multiplication(*args):
    requirements.add("multiplication")
    return []
def get_value(*args):
    requirements.add("get")
    return []
def fill_int_column(*args):
    requirements.add("fill_int_column")
    return []
def fill_float_column(*args):
    requirements.add("fill_float_column")
    return []
def fill_Boolean_column(*args):
    requirements.add("fill_bool_column")
    return []
def fill_string_column(*args):
    requirements.add("fill_string_column")
    return []
def map_column(*args):
    requirements.add("map")
    return []
def round_column(*args):
    requirements.add("round")
    return []
def cast_to_int(*args):
    requirements.add("to_int")
    return []
def cast_to_float(*args):
    requirements.add("to_float")
    return []
def cast_to_string(*args):
    requirements.add("to_string")
    return []
def cast_to_Boolean(*args):
    requirements.add("to_bool")
    return []
def is_empty(*args):
    requirements.add("is_empty")
    return []
def get_null(*args):
    requirements.add("get_null")
    return []
def sort_rows(*args):
    requirements.add("sort")
    return []
def first_rows(*args):
    requirements.add("first_rows")
    return []
def substring(*args):
    requirements.add("substring")
    return []
def addition(*args):
    requirements.add("addition")
    return []
def subtraction(*args):
    requirements.add("subtraction")
    return []
def division(*args):
    requirements.add("division")
    return []
def filter_table(*args):
    requirements.add("filter")
    return []
def less_than(*args):
    requirements.add("less_than")
    return []
def greater_than(*args):
    requirements.add("greater_than")
    return []
def equal(*args):
    requirements.add("equal_to")
    return []
def not_equal(*args):
    requirements.add("not_equal_to")
    return []
def less_than_or_equal(*args):
    requirements.add("less_than_or_equal")
    return []
def greater_than_or_equal(*args):
    requirements.add("greater_than_or_equal")
    return []
def logical_and(*args):
    requirements.add("and")
    return []
def logical_or(*args):
    requirements.add("or")
    return []
def logical_not(*args):
    requirements.add("not")
    return []
def calculate_sum(*args):
    requirements.add("sum")
    return []
def calculate_min(*args):
    requirements.add("min")
    return []
def calculate_max(*args):
    requirements.add("max")
    return []
def calculate_avg(*args):
    requirements.add("avg")
    return []
def count_distinct(*args):
    requirements.add("count_distinct")
    return []
def if_else(*args):
    requirements.add("case")
    return []
def group_by_sum(*args):
    requirements.add("grouped_sum")
    return []
def group_by_min(*args):
    requirements.add("grouped_min")
    return []
def group_by_max(*args):
    requirements.add("grouped_max")
    return []
def group_by_avg(*args):
    requirements.add("grouped_avg")
    return []
def group_by_count(*args):
    requirements.add("grouped_count")
    return []
def equality_join(*args):
    requirements.add("equi_join")
    return []
def left_outer_join(*args):
    requirements.add("left_join")
    return []
def right_outer_join(*args):
    requirements.add("right_join")
    return []
def full_outer_join(*args):
    requirements.add("full_join")
    return []
'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
import datetime
import re
'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
def cast_to_int_round(*args):
    round_column()
    cast_to_int()

def is_empty(*args):
    """ Code generator visits some branches only for non-empty tables. 
    
    Returns:
        False to ensure everything is visited during tracing
    """
    requirements.add('is_empty')
    return False

def nr_rows(*args):
    """ Code generator visits some branches only for non-empty tables.
    
    Returns:
        True to ensure that all dependencies are traced
    """
    requirements.add('nr_rows')
    return 1

def if_else(*args):
    """ Visit both branches of if-statement during tracing.
    
    Args:
        if_val: expression result if condition is satisfied
        else_val: expression result if condition is not satisfied
    
    Returns:
        dummy value
    """
    requirements.add('case')
    # for val in [if_val, else_val]:
        # if callable(val):
            # val()
        # else:
            # val
    return []

def fix_nulls(inputs, result, result_type):
    nr_rows()
    is_null()
    multiway_or()
    get_null()
    if_else()

def multiway_and(*args):
    nr_rows()
    fill_Boolean_column()
    logical_and()
    return []

def multiway_or(*args):
    nr_rows()
    fill_Boolean_column()
    logical_or()
    return []

def grouped_count(*args):
    get_column()
    logical_not()
    is_null()
    map_column()
    table_cardinality()
    fill_Boolean_column()
    fill_int_column()
    fill_float_column()
    fill_string_column()
    create_table()
    group_by_sum()
    set_column()
    group_by_sum()
    return []

def multiply_by_scalar(*args):
    nr_rows()
    fill_Boolean_column()
    fill_int_column()
    fill_float_column()
    fill_string_column()
    multiplication()
    return []

def scale_columns(columns, types):
    nr_rows()
    get_value()
    fill_Boolean_column()
    fill_int_column()
    fill_float_column()
    fill_string_column()
    return columns

def scale_to_table(column, col_type, table):
    get_column()
    nr_rows()
    get_value()
    fill_Boolean_column()
    fill_int_column()
    fill_float_column()
    fill_string_column()
    return column, table

def smart_date_extract(*args):
    map_column()
    return []

def smart_padding(*args):
    map_column()
    return []

def sort_wrapper(*args):
    get_column()
    multiply_by_scalar()
    set_column()
    sort_rows()
    return []

def table_cardinality(*args):
    is_empty()
    nr_rows()
    get_column()
    return []

def ungrouped_count(*args):
    get_column()
    logical_not()
    multiway_or()
    is_null()
    filter_table()
    count_distinct()
    table_cardinality()
    return []
# Operation ID: 0; Operator: LogicalTableScan
result_0 = load_from_csv("tpch_sf0001/supplier.csv")
col = get_column(result_0,0)
col = cast_to_int_round(col)
set_column(result_0,0,col)
col = get_column(result_0,1)
col = cast_to_string(col)
set_column(result_0,1,col)
col = get_column(result_0,2)
col = cast_to_string(col)
set_column(result_0,2,col)
col = get_column(result_0,3)
col = cast_to_int_round(col)
set_column(result_0,3,col)
col = get_column(result_0,4)
col = cast_to_string(col)
set_column(result_0,4,col)
col = get_column(result_0,5)
col = cast_to_int_round(col)
set_column(result_0,5,col)
col = get_column(result_0,6)
col = cast_to_string(col)
set_column(result_0,6,col)
last_result = result_0
# Operation ID: 1; Operator: LogicalTableScan
result_1 = load_from_csv("tpch_sf0001/nation.csv")
col = get_column(result_1,0)
col = cast_to_int_round(col)
set_column(result_1,0,col)
col = get_column(result_1,1)
col = cast_to_string(col)
set_column(result_1,1,col)
col = get_column(result_1,2)
col = cast_to_int_round(col)
set_column(result_1,2,col)
col = get_column(result_1,3)
col = cast_to_string(col)
set_column(result_1,3,col)
last_result = result_1
# Operation ID: 2; Operator: LogicalFilter
in_rel_1 = result_1
p_idx = cast_to_Boolean(fix_nulls(scale_columns([cast_to_string(get_column(in_rel_1,1)),cast_to_string(fill_string_column('CANADA                   ',1))], ['string', 'string']),equal(*scale_columns([cast_to_string(get_column(in_rel_1,1)),cast_to_string(fill_string_column('CANADA                   ',1))], ['string', 'string'])),"Boolean"))
p_idx = scale_to_table(p_idx, "Boolean", in_rel_1)
result_2 = filter_table(in_rel_1, p_idx)
col = get_column(result_2,0)
col = cast_to_int_round(col)
set_column(result_2,0,col)
col = get_column(result_2,1)
col = cast_to_string(col)
set_column(result_2,1,col)
col = get_column(result_2,2)
col = cast_to_int_round(col)
set_column(result_2,2,col)
col = get_column(result_2,3)
col = cast_to_string(col)
set_column(result_2,3,col)
last_result = result_2
# Operation ID: 3; Operator: LogicalJoin
in_rel_1 = result_0
in_rel_2 = result_2
result_3 = equality_join(in_rel_1, in_rel_2, [3], [0])
col = get_column(result_3,0)
col = cast_to_int_round(col)
set_column(result_3,0,col)
col = get_column(result_3,1)
col = cast_to_string(col)
set_column(result_3,1,col)
col = get_column(result_3,2)
col = cast_to_string(col)
set_column(result_3,2,col)
col = get_column(result_3,3)
col = cast_to_int_round(col)
set_column(result_3,3,col)
col = get_column(result_3,4)
col = cast_to_string(col)
set_column(result_3,4,col)
col = get_column(result_3,5)
col = cast_to_int_round(col)
set_column(result_3,5,col)
col = get_column(result_3,6)
col = cast_to_string(col)
set_column(result_3,6,col)
col = get_column(result_3,7)
col = cast_to_int_round(col)
set_column(result_3,7,col)
col = get_column(result_3,8)
col = cast_to_string(col)
set_column(result_3,8,col)
col = get_column(result_3,9)
col = cast_to_int_round(col)
set_column(result_3,9,col)
col = get_column(result_3,10)
col = cast_to_string(col)
set_column(result_3,10,col)
last_result = result_3
# Operation ID: 4; Operator: LogicalTableScan
result_4 = load_from_csv("tpch_sf0001/partsupp.csv")
col = get_column(result_4,0)
col = cast_to_int_round(col)
set_column(result_4,0,col)
col = get_column(result_4,1)
col = cast_to_int_round(col)
set_column(result_4,1,col)
col = get_column(result_4,2)
col = cast_to_int_round(col)
set_column(result_4,2,col)
col = get_column(result_4,3)
col = cast_to_int_round(col)
set_column(result_4,3,col)
col = get_column(result_4,4)
col = cast_to_string(col)
set_column(result_4,4,col)
last_result = result_4
# Operation ID: 5; Operator: LogicalTableScan
result_5 = load_from_csv("tpch_sf0001/part.csv")
col = get_column(result_5,0)
col = cast_to_int_round(col)
set_column(result_5,0,col)
col = get_column(result_5,1)
col = cast_to_string(col)
set_column(result_5,1,col)
col = get_column(result_5,2)
col = cast_to_string(col)
set_column(result_5,2,col)
col = get_column(result_5,3)
col = cast_to_string(col)
set_column(result_5,3,col)
col = get_column(result_5,4)
col = cast_to_string(col)
set_column(result_5,4,col)
col = get_column(result_5,5)
col = cast_to_int_round(col)
set_column(result_5,5,col)
col = get_column(result_5,6)
col = cast_to_string(col)
set_column(result_5,6,col)
col = get_column(result_5,7)
col = cast_to_int_round(col)
set_column(result_5,7,col)
col = get_column(result_5,8)
col = cast_to_string(col)
set_column(result_5,8,col)
last_result = result_5
# Operation ID: 6; Operator: LogicalFilter
in_rel_1 = result_5
p_idx = cast_to_Boolean(map_column(cast_to_string(get_column(in_rel_1,1)), lambda s:re.match(get_value(cast_to_string(fill_string_column('forest%',1)),0).replace('%', '.*'), s) is not None))
p_idx = scale_to_table(p_idx, "Boolean", in_rel_1)
result_6 = filter_table(in_rel_1, p_idx)
col = get_column(result_6,0)
col = cast_to_int_round(col)
set_column(result_6,0,col)
col = get_column(result_6,1)
col = cast_to_string(col)
set_column(result_6,1,col)
col = get_column(result_6,2)
col = cast_to_string(col)
set_column(result_6,2,col)
col = get_column(result_6,3)
col = cast_to_string(col)
set_column(result_6,3,col)
col = get_column(result_6,4)
col = cast_to_string(col)
set_column(result_6,4,col)
col = get_column(result_6,5)
col = cast_to_int_round(col)
set_column(result_6,5,col)
col = get_column(result_6,6)
col = cast_to_string(col)
set_column(result_6,6,col)
col = get_column(result_6,7)
col = cast_to_int_round(col)
set_column(result_6,7,col)
col = get_column(result_6,8)
col = cast_to_string(col)
set_column(result_6,8,col)
last_result = result_6
# Operation ID: 7; Operator: LogicalAggregate
in_rel_1 = result_6
# LogicalAggregate: aggs: []; groups [0]
result_7 = create_table(result_cols)
col = get_column(result_7,0)
col = cast_to_int_round(col)
set_column(result_7,0,col)
last_result = result_7
# Operation ID: 8; Operator: LogicalJoin
in_rel_1 = result_4
in_rel_2 = result_7
result_8 = equality_join(in_rel_1, in_rel_2, [0], [0])
col = get_column(result_8,0)
col = cast_to_int_round(col)
set_column(result_8,0,col)
col = get_column(result_8,1)
col = cast_to_int_round(col)
set_column(result_8,1,col)
col = get_column(result_8,2)
col = cast_to_int_round(col)
set_column(result_8,2,col)
col = get_column(result_8,3)
col = cast_to_int_round(col)
set_column(result_8,3,col)
col = get_column(result_8,4)
col = cast_to_string(col)
set_column(result_8,4,col)
col = get_column(result_8,5)
col = cast_to_int_round(col)
set_column(result_8,5,col)
last_result = result_8
# Operation ID: 9; Operator: LogicalTableScan
result_9 = load_from_csv("tpch_sf0001/lineitem.csv")
col = get_column(result_9,0)
col = cast_to_int_round(col)
set_column(result_9,0,col)
col = get_column(result_9,1)
col = cast_to_int_round(col)
set_column(result_9,1,col)
col = get_column(result_9,2)
col = cast_to_int_round(col)
set_column(result_9,2,col)
col = get_column(result_9,3)
col = cast_to_int_round(col)
set_column(result_9,3,col)
col = get_column(result_9,4)
col = cast_to_int_round(col)
set_column(result_9,4,col)
col = get_column(result_9,5)
col = cast_to_int_round(col)
set_column(result_9,5,col)
col = get_column(result_9,6)
col = cast_to_int_round(col)
set_column(result_9,6,col)
col = get_column(result_9,7)
col = cast_to_int_round(col)
set_column(result_9,7,col)
col = get_column(result_9,8)
col = cast_to_string(col)
set_column(result_9,8,col)
col = get_column(result_9,9)
col = cast_to_string(col)
set_column(result_9,9,col)
col = get_column(result_9,10)
col = cast_to_int_round(col)
set_column(result_9,10,col)
col = get_column(result_9,11)
col = cast_to_int_round(col)
set_column(result_9,11,col)
col = get_column(result_9,12)
col = cast_to_int_round(col)
set_column(result_9,12,col)
col = get_column(result_9,13)
col = cast_to_string(col)
set_column(result_9,13,col)
col = get_column(result_9,14)
col = cast_to_string(col)
set_column(result_9,14,col)
col = get_column(result_9,15)
col = cast_to_string(col)
set_column(result_9,15,col)
last_result = result_9
# Operation ID: 10; Operator: LogicalFilter
in_rel_1 = result_9
p_idx = cast_to_Boolean(multiway_and(scale_columns([cast_to_Boolean(fix_nulls(scale_columns([cast_to_int_round(get_column(in_rel_1,10)),cast_to_int_round(fill_int_column(8766,1))], ['int', 'int']),greater_than_or_equal(*scale_columns([cast_to_int_round(get_column(in_rel_1,10)),cast_to_int_round(fill_int_column(8766,1))], ['int', 'int'])),"Boolean")), cast_to_Boolean(fix_nulls(scale_columns([cast_to_int_round(get_column(in_rel_1,10)),cast_to_int_round(fill_int_column(9131,1))], ['int', 'int']),less_than(*scale_columns([cast_to_int_round(get_column(in_rel_1,10)),cast_to_int_round(fill_int_column(9131,1))], ['int', 'int'])),"Boolean"))], ['Boolean', 'Boolean'])))
p_idx = scale_to_table(p_idx, "Boolean", in_rel_1)
result_10 = filter_table(in_rel_1, p_idx)
col = get_column(result_10,0)
col = cast_to_int_round(col)
set_column(result_10,0,col)
col = get_column(result_10,1)
col = cast_to_int_round(col)
set_column(result_10,1,col)
col = get_column(result_10,2)
col = cast_to_int_round(col)
set_column(result_10,2,col)
col = get_column(result_10,3)
col = cast_to_int_round(col)
set_column(result_10,3,col)
col = get_column(result_10,4)
col = cast_to_int_round(col)
set_column(result_10,4,col)
col = get_column(result_10,5)
col = cast_to_int_round(col)
set_column(result_10,5,col)
col = get_column(result_10,6)
col = cast_to_int_round(col)
set_column(result_10,6,col)
col = get_column(result_10,7)
col = cast_to_int_round(col)
set_column(result_10,7,col)
col = get_column(result_10,8)
col = cast_to_string(col)
set_column(result_10,8,col)
col = get_column(result_10,9)
col = cast_to_string(col)
set_column(result_10,9,col)
col = get_column(result_10,10)
col = cast_to_int_round(col)
set_column(result_10,10,col)
col = get_column(result_10,11)
col = cast_to_int_round(col)
set_column(result_10,11,col)
col = get_column(result_10,12)
col = cast_to_int_round(col)
set_column(result_10,12,col)
col = get_column(result_10,13)
col = cast_to_string(col)
set_column(result_10,13,col)
col = get_column(result_10,14)
col = cast_to_string(col)
set_column(result_10,14,col)
col = get_column(result_10,15)
col = cast_to_string(col)
set_column(result_10,15,col)
last_result = result_10
# Operation ID: 11; Operator: LogicalProject
in_rel_1 = result_10
result_cols = []
column = cast_to_int_round(get_column(in_rel_1,1))
column = scale_to_table(column, "int", in_rel_1)
result_cols += [column]
column = cast_to_int_round(get_column(in_rel_1,2))
column = scale_to_table(column, "int", in_rel_1)
result_cols += [column]
column = cast_to_int_round(get_column(in_rel_1,4))
column = scale_to_table(column, "int", in_rel_1)
result_cols += [column]
result_11 = create_table(result_cols)
col = get_column(result_11,0)
col = cast_to_int_round(col)
set_column(result_11,0,col)
col = get_column(result_11,1)
col = cast_to_int_round(col)
set_column(result_11,1,col)
col = get_column(result_11,2)
col = cast_to_int_round(col)
set_column(result_11,2,col)
last_result = result_11
# Operation ID: 12; Operator: LogicalAggregate
in_rel_1 = result_11
# LogicalAggregate: aggs: [{'agg': {'name': 'SUM', 'kind': 'SUM', 'syntax': 'FUNCTION'}, 'type': {'type': 'DECIMAL', 'nullable': False, 'precision': 19, 'scale': 2}, 'distinct': False, 'operands': [2], 'name': None}]; groups [0, 1]
agg_tbl = group_by_sum(in_rel_1, 2, [0, 1])
agg_tbl = sort_rows(agg_tbl, [0, 1])
result_cols = [get_column(agg_tbl, i) for i in range(2)]
result_col = get_column(agg_tbl, 2)
result_cols += [result_col]
result_12 = create_table(result_cols)
col = get_column(result_12,0)
col = cast_to_int_round(col)
set_column(result_12,0,col)
col = get_column(result_12,1)
col = cast_to_int_round(col)
set_column(result_12,1,col)
col = get_column(result_12,2)
col = cast_to_int_round(col)
set_column(result_12,2,col)
last_result = result_12
# Operation ID: 13; Operator: LogicalJoin
in_rel_1 = result_8
in_rel_2 = result_12
result_13 = equality_join(in_rel_1, in_rel_2, [0, 1], [0, 1])
in_rel_1 = result_13
p_idx = multiway_and([cast_to_Boolean(fix_nulls(scale_columns([multiply_by_scalar(cast_to_int_round(get_column(in_rel_1,2)), 1e3),cast_to_int_round(fix_nulls(scale_columns([cast_to_int_round(fill_int_column(round(0.5*1e1),1)),cast_to_int_round(get_column(in_rel_1,8))], ['int', 'int']),multiplication(*scale_columns([cast_to_int_round(fill_int_column(round(0.5*1e1),1)),cast_to_int_round(get_column(in_rel_1,8))], ['int', 'int'])),"int"))], ['int', 'int']),greater_than(*scale_columns([multiply_by_scalar(cast_to_int_round(get_column(in_rel_1,2)), 1e3),cast_to_int_round(fix_nulls(scale_columns([cast_to_int_round(fill_int_column(round(0.5*1e1),1)),cast_to_int_round(get_column(in_rel_1,8))], ['int', 'int']),multiplication(*scale_columns([cast_to_int_round(fill_int_column(round(0.5*1e1),1)),cast_to_int_round(get_column(in_rel_1,8))], ['int', 'int'])),"int"))], ['int', 'int'])),"Boolean"))])
result_13 = filter_table(result_13, p_idx)
col = get_column(result_13,0)
col = cast_to_int_round(col)
set_column(result_13,0,col)
col = get_column(result_13,1)
col = cast_to_int_round(col)
set_column(result_13,1,col)
col = get_column(result_13,2)
col = cast_to_int_round(col)
set_column(result_13,2,col)
col = get_column(result_13,3)
col = cast_to_int_round(col)
set_column(result_13,3,col)
col = get_column(result_13,4)
col = cast_to_string(col)
set_column(result_13,4,col)
col = get_column(result_13,5)
col = cast_to_int_round(col)
set_column(result_13,5,col)
col = get_column(result_13,6)
col = cast_to_int_round(col)
set_column(result_13,6,col)
col = get_column(result_13,7)
col = cast_to_int_round(col)
set_column(result_13,7,col)
col = get_column(result_13,8)
col = cast_to_int_round(col)
set_column(result_13,8,col)
last_result = result_13
# Operation ID: 14; Operator: LogicalProject
in_rel_1 = result_13
result_cols = []
column = cast_to_int_round(get_column(in_rel_1,0))
column = scale_to_table(column, "int", in_rel_1)
result_cols += [column]
column = cast_to_int_round(get_column(in_rel_1,1))
column = scale_to_table(column, "int", in_rel_1)
result_cols += [column]
column = cast_to_int_round(get_column(in_rel_1,2))
column = scale_to_table(column, "int", in_rel_1)
result_cols += [column]
column = cast_to_int_round(get_column(in_rel_1,3))
column = scale_to_table(column, "int", in_rel_1)
result_cols += [column]
column = cast_to_string(get_column(in_rel_1,4))
column = scale_to_table(column, "string", in_rel_1)
result_cols += [column]
column = cast_to_int_round(get_column(in_rel_1,5))
column = scale_to_table(column, "int", in_rel_1)
result_cols += [column]
column = cast_to_int_round(cast_to_int_round(get_column(in_rel_1,6)))
column = scale_to_table(column, "int", in_rel_1)
result_cols += [column]
column = cast_to_int_round(cast_to_int_round(get_column(in_rel_1,7)))
column = scale_to_table(column, "int", in_rel_1)
result_cols += [column]
column = cast_to_int_round(cast_to_int_round(get_column(in_rel_1,8)))
column = scale_to_table(column, "int", in_rel_1)
result_cols += [column]
result_14 = create_table(result_cols)
col = get_column(result_14,0)
col = cast_to_int_round(col)
set_column(result_14,0,col)
col = get_column(result_14,1)
col = cast_to_int_round(col)
set_column(result_14,1,col)
col = get_column(result_14,2)
col = cast_to_int_round(col)
set_column(result_14,2,col)
col = get_column(result_14,3)
col = cast_to_int_round(col)
set_column(result_14,3,col)
col = get_column(result_14,4)
col = cast_to_string(col)
set_column(result_14,4,col)
col = get_column(result_14,5)
col = cast_to_int_round(col)
set_column(result_14,5,col)
col = get_column(result_14,6)
col = cast_to_int_round(col)
set_column(result_14,6,col)
col = get_column(result_14,7)
col = cast_to_int_round(col)
set_column(result_14,7,col)
col = get_column(result_14,8)
col = cast_to_int_round(col)
set_column(result_14,8,col)
last_result = result_14
# Operation ID: 15; Operator: LogicalAggregate
in_rel_1 = result_14
# LogicalAggregate: aggs: []; groups [1]
result_15 = create_table(result_cols)
col = get_column(result_15,0)
col = cast_to_int_round(col)
set_column(result_15,0,col)
last_result = result_15
# Operation ID: 16; Operator: LogicalJoin
in_rel_1 = result_3
in_rel_2 = result_15
result_16 = equality_join(in_rel_1, in_rel_2, [0], [0])
col = get_column(result_16,0)
col = cast_to_int_round(col)
set_column(result_16,0,col)
col = get_column(result_16,1)
col = cast_to_string(col)
set_column(result_16,1,col)
col = get_column(result_16,2)
col = cast_to_string(col)
set_column(result_16,2,col)
col = get_column(result_16,3)
col = cast_to_int_round(col)
set_column(result_16,3,col)
col = get_column(result_16,4)
col = cast_to_string(col)
set_column(result_16,4,col)
col = get_column(result_16,5)
col = cast_to_int_round(col)
set_column(result_16,5,col)
col = get_column(result_16,6)
col = cast_to_string(col)
set_column(result_16,6,col)
col = get_column(result_16,7)
col = cast_to_int_round(col)
set_column(result_16,7,col)
col = get_column(result_16,8)
col = cast_to_string(col)
set_column(result_16,8,col)
col = get_column(result_16,9)
col = cast_to_int_round(col)
set_column(result_16,9,col)
col = get_column(result_16,10)
col = cast_to_string(col)
set_column(result_16,10,col)
col = get_column(result_16,11)
col = cast_to_int_round(col)
set_column(result_16,11,col)
last_result = result_16
# Operation ID: 17; Operator: LogicalProject
in_rel_1 = result_16
result_cols = []
column = cast_to_string(get_column(in_rel_1,1))
column = scale_to_table(column, "string", in_rel_1)
result_cols += [column]
column = cast_to_string(get_column(in_rel_1,2))
column = scale_to_table(column, "string", in_rel_1)
result_cols += [column]
result_17 = create_table(result_cols)
col = get_column(result_17,0)
col = cast_to_string(col)
set_column(result_17,0,col)
col = get_column(result_17,1)
col = cast_to_string(col)
set_column(result_17,1,col)
last_result = result_17
# Operation ID: 18; Operator: LogicalSort
in_rel_1 = result_17
result_18 = in_rel_1
sort_cols = [0]
ascending = [True]
result_18 = sort_wrapper(result_18, sort_cols, ascending)
col = get_column(result_18,0)
col = cast_to_string(col)
set_column(result_18,0,col)
col = get_column(result_18,1)
col = cast_to_string(col)
set_column(result_18,1,col)
last_result = result_18
col = get_column(last_result,0)
col = smart_padding(col, 25)
set_column(last_result, 0, col)
col = get_column(last_result,1)
set_column(last_result, 1, col)
write_to_csv(last_result, "dummy_path")