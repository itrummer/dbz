'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
t = load_from_csv('test_input/test1.csv')
s = sort_rows(t, [3])
write_to_csv(s, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/test1_sorted.csv')