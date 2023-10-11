'''
Created on Nov 12, 2022

@author: immanueltrummer
'''
c = fill_int_column(3, 10)
v = get_value(c, 3)
assert isinstance(v, int), f'Should be of type int but is {type(v)}'
assert v == 3, f'Should be 3 but is {v}'