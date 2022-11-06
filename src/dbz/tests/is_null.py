'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c = fill_int_column(1, 10)
nc = fill_int_column(get_null(), 10)
assert not get_value(is_null(c), 0)
assert get_value(is_null(nc), 0)