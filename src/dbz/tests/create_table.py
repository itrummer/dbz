'''
Created on Nov 8, 2022

@author: immanueltrummer
'''
c = fill_int_column(1, 0)
t = create_table([c])
assert is_empty(t), f'Not empty: {t}'
assert check_table_type(t), f'Unexpected type: {type(t)}'

c = fill_int_column(1, 10)
t2 = create_table([c, c])
assert not is_empty(t2), f'Should not be empty'
assert check_table_type(t2), f'Unexpected type: {type(t2)}'