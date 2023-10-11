'''
Created on Nov 10, 2022

@author: immanueltrummer
'''
ca = fill_int_column(1, 7)
ag = calculate_sum(ca)
rc = fill_int_column(ag, 1)
t = create_table([rc])
write_to_csv(t, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/int7_1.csv')