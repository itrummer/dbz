'''
Created on Nov 13, 2022

@author: immanueltrummer
'''
c = fill_string_column('###This is a test####')
r = substring(c, 4, 14)
t = create_table([r])
write_to_csv('test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/string.csv')