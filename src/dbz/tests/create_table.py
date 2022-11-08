'''
Created on Nov 8, 2022

@author: immanueltrummer
'''
t = create_table([])
assert is_empty(t)
assert check_table_type(t)

c = fill_int_column(1, 10)
t2 = create_table([c, c])
assert not is_empty(t2)
assert check_table_type(t2)