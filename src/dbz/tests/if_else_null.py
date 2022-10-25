'''
Created on Oct 22, 2022

@author: immanueltrummer
'''
c = fill_Boolean_column(True, 1)
n = fill_int_column(get_null(), 1)

r = if_else(c,c,n)
r = is_null(r)
assert not get_value(r,0)

r = if_else(c,n,c)
r = is_null(r)
assert get_value(r,0)

r = if_else(n,c,n)
r = is_null(r)
assert get_value(r,0)

r = if_else(n,n,c)
r = is_null(r)
assert not get_value(r,0)