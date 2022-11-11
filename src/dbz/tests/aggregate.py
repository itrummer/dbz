'''
Created on Nov 10, 2022

@author: immanueltrummer
'''
ca = fill_float_column(1.5, 5)
ag = calculate_<SubstituteBy:max|min|avg>(ca)
t = create_table([ag])
write_to_csv(t, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/float1.5_1.csv')