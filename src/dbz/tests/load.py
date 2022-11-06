'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
t = load_from_csv('test_data/test1.csv')
assert check_table_type(t)