'''
Created on Nov 13, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(2, 10)
c2 = fill_int_column(5, 10)

r = greater_than(c1, c2)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/false10.csv')

r = greater_than(c2, c1)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/true10.csv')