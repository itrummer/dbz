'''
Created on Nov 10, 2022

@author: immanueltrummer
'''
ca = fill_float_column(1.5, 5)
ag = calculate_<SubstituteBy:max|min|avg>(ca)
rc = fill_float_column(ag, 1)
t = create_table([rc])
write_to_csv(t, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/float1.5_1.csv')