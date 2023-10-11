'''
Created on Nov 12, 2022

@author: immanueltrummer
'''
c = fill_float_column(1.3, 10)
v = get_value(c, 3)
assert isinstance(v, float), f'Should be float but is {type(v)}'
assert v == 1.3, f'Should be 1.3 but is {v}'