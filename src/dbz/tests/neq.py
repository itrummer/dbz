'''
Created on Nov 13, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(2, 10)
c2 = fill_int_column(5, 10)

r = not_equal(c1, c2)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/true10.csv')

r = not_equal(c1, c1)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/false10.csv')