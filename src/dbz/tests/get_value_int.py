'''
Created on Nov 12, 2022

@author: immanueltrummer
'''
c = fill_int_column(3, 10)
v = get_value(c, 3)
assert isinstance(v, int)
assert v == 3