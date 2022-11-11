'''
Created on Oct 30, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(1,10)
c2 = fill_int_column(0,10)
t1 = create_table([c1, c2])
t2 = create_table([c1, c2])

r = left_outer_join(t1, t2, 2, [1], [1])
write_to_csv(r, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/1010_100.csv')

r = left_outer_join(t1, t2, 2, [0], [0])
write_to_csv(r, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/1010_100.csv')

r = left_outer_join(t1, t2, 2, [1], [0])
write_to_csv(r, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/10nullnull_10.csv')

r = left_outer_join(t1, t2, 2, [0], [1])
write_to_csv(r, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/10nullnull_10.csv')