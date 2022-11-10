'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(2, 10)
c2 = fill_int_column(3, 10)
t = create_table([c1, c1, c2])

write_to_csv(count_distinct(t, [0]), 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/int1_1x3.csv')

write_to_csv(count_distinct(t, [0, 1]), 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/int1_1x3.csv')

write_to_csv(count_distinct(t, [0, 1, 2]), 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/int1_1x3.csv')