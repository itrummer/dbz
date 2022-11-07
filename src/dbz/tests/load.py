'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
t = load_from_csv('test_data/test1.csv')
assert check_table_type(t)

c = get_column(t, 3)
n = is_null(c)
assert get_value(n, 0)
assert not get_value(n, 1)
assert get_value(n, 0)