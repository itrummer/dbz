'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c = fill_float_column(1.5, 10)
t = create_table([c])
write_to_csv(t, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/float1.5_10.csv')