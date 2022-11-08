'''
Created on Nov 7, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(1, 10)
c2 = fill_int_column(2, 10)
t1 = create_table([c1, c1])
t2 = set_column(t1, 0, c2)

#assert get_value(get_column(t1, 0), 0) == 1
#assert get_value(get_column(t1, 1), 0) == 1
assert get_value(get_column(t2, 0), 0) == 2
assert get_value(get_column(t2, 1), 0) == 1