'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(2, 10)
c2 = fill_int_column(3, 10)
t = create_table([c1, c1, c2])

d = count_distinct(t, [0])
dc = fill_int_column(d, 1)
dt = create_table([dc])
write_to_csv(dt, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/int1_1.csv')

d = count_distinct(t, [0, 1])
dc = fill_int_column(d, 1)
dt = create_table([dc])
write_to_csv(dt, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/int1_1.csv')

d = count_distinct(t, [0, 1, 2])
dc = fill_int_column(d, 1)
dt = create_table([dc])
write_to_csv(dt, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/int1_1.csv')