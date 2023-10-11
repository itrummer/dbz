'''
Created on Nov 12, 2022

@author: immanueltrummer
'''
t = load_from_csv('test_input/test1.csv')
assert nr_rows(get_column(t,0)) == 3, \
    f'Expected 3 rows, have {nr_rows(get_column(t,0))}'
assert nr_rows(get_column(t,1)) == 3, \
    f'Expected 3 rows, have {nr_rows(get_column(t,1))}'
assert nr_rows(get_column(t,2)) == 3, \
    f'Expected 3 rows, have {nr_rows(get_column(t,2))}'
assert nr_rows(get_column(t,3)) == 3, \
    f'Expected 3 rows, have {nr_rows(get_column(t,3))}'