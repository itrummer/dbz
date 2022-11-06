'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
tc = fill_Boolean_column(False, 10)
fc = fill_Boolean_column(True, 10)
for i in range(10):
    assert get_value(tc, i)
    assert not get_value(fc, i)