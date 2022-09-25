'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
def multiway_and(*args):
    nr_rows()
    fill_column()
    logical_and()

def multiway_or(*args):
    nr_rows()
    fill_column()
    logical_or()

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

def multiply_by_scalar(*args):
    nr_rows()
    fill_column()
    multiplication()

def scale_columns(*args):
    nr_rows()
    get_value()
    fill_column()

def scale_to_table(*args):
    get_column()
    nr_rows()
    get_value()
    fill_column()

def smart_date_extract(*args):
    map_column()

def smart_padding(*args):
    map_column()

def sort_wrapper(*args):
    get_column()
    multiply_by_scalar()
    set_column()
    sort_rows()    

def table_cardinality(*args):
    is_empty()
    nr_rows()
    get_column()

def ungrouped_count(*args):
    get_column()
    logical_not()
    multiway_or()
    is_null()
    filter_table()
    count_distinct()
    table_cardinality()