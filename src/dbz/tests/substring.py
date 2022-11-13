'''
Created on Nov 13, 2022

@author: immanueltrummer
'''
c = fill_string_column('###This is a test####', 10)
r = substring(c, 4, 14)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/string10.csv')