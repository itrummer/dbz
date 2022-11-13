'''
Created on Nov 12, 2022

@author: immanueltrummer
'''
c = fill_float_column(1.3, 10)
v = get_value(c, 3)
assert isinstance(v, float)
assert v == 1.3