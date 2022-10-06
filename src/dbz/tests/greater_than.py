'''
Created on Oct 5, 2022

@author: immanueltrummer
'''
c0 = fill_column(get_null(), 10)
c1 = fill_column(2, 10)
c2 = fill_column(3, 10)
c3 = fill_column(-1, 10)
b1 = greater_than(c0, c1)
b2 = greater_than(c1, c2)
b3 = greater_than(c2, c3)
last_result = create_table([b1, b2, b3, c0])