'''
Created on Nov 13, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(10, 10)
c2 = fill_int_column(3, 10)
r = subtraction(c1, c2)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/int7_10.csv')