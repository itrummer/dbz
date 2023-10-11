'''
Created on Nov 12, 2022

@author: immanueltrummer
'''
c = fill_float_column(7.4, 10)
r = round_column(c)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/int7_10.csv')