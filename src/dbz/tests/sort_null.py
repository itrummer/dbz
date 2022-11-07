'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
t = load_from_csv('test_data/test1.csv')
s = sort_rows(t, [3])
c = get_column(s, 0)
v = get_value(c, 0)
assert v == 2