'''
Created on Oct 22, 2022

@author: immanueltrummer
'''
c = fill_int_column(True, 10)
r = if_else(c,c,c)
assert check_column_type(r)