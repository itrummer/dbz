'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c = fill_int_column(1, 10)
t = create_table([c, c])
a = group_by_sum(t, 0, [1])
write_to_csv(a, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/int1-10_1.csv')