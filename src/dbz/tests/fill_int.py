'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c = fill_int_column(7,10)
for i in range(10):
    assert get_value(c, i) == 7