'''
Created on Nov 10, 2022

@author: immanueltrummer
'''
ca = fill_float_column(1, 7)
ag = calculate_sum(ca)
t = create_table([ag])
write_to_csv(t, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/int7_1.csv')