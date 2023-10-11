'''
Created on Nov 12, 2022

@author: immanueltrummer
'''
c = fill_Boolean_column(True, 10)
v = get_value(c, 3)
assert isinstance(v, bool), f'Unexpected type: {type(v)}'
assert v == True, f'Should be True but is {v}'