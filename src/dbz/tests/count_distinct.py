'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(2, 10)
c2 = fill_int_column(3, 10)
t = create_table([c1, c1, c2])
assert count_distinct(t, [0]) == 1
assert count_distinct(t, [0, 1]) == 1
assert count_distinct(t, [0, 1, 2]) == 1