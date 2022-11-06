'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c = fill_string_column('this is a test', 10)
for i in range(10):
    assert get_value(c, i) == 'this is a test'