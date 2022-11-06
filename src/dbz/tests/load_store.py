'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c = fill_int_column(1, 10)
t = create_table([c, c])
write_to_csv(t, 'dummy.csv')
t = load_from_csv('dummy.csv')
assert check_table_type(t)