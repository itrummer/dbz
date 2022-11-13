'''
Created on Nov 13, 2022

@author: immanueltrummer
'''
c = fill_float_column(7.4, 10)
r = floor(c)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/int7_10.csv')