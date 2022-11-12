'''
Created on Nov 12, 2022

@author: immanueltrummer
'''
t = load_from_csv('test_input/test1.csv')
assert nr_rows(get_column(t,0)) == 3
assert nr_rows(get_column(t,1)) == 3
assert nr_rows(get_column(t,2)) == 3
assert nr_rows(get_column(t,3)) == 3