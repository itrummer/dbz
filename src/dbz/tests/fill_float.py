'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c = fill_float_column(1.5, 10)
for i in range(10):
    assert get_value(c, i) == 1.5