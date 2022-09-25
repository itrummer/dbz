'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
def multiway_and(*args):
    nr_rows()
    fill_column()
    logical_and()
    return []

def multiway_or(*args):
    nr_rows()
    fill_column()
    logical_or()
    return []

def grouped_count(*args):
    get_column()
    logical_not()
    is_null()
    map_column()
    table_cardinality()
    fill_column()
    create_table()
    group_by_sum()
    set_column()
    group_by_sum()
    return []

def multiply_by_scalar(*args):
    nr_rows()
    fill_column()
    multiplication()
    return []

def scale_columns(*args):
    nr_rows()
    get_value()
    fill_column()
    return []

def scale_to_table(*args):
    get_column()
    nr_rows()
    get_value()
    fill_column()
    return []

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