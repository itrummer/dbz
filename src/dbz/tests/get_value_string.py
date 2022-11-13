'''
Created on Nov 12, 2022

@author: immanueltrummer
'''
c = fill_string_column('This is a test', 10)
v = get_value(c, 3)
assert isinstance(v, str)
assert v == 'This is a test'