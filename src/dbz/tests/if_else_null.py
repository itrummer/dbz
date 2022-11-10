'''
Created on Oct 22, 2022

@author: immanueltrummer
'''
b_t = fill_Boolean_column(True, 1)
b_n = fill_Boolean_column(get_null(), 1)
i_1 = fill_int_column(1, 1)
i_n = fill_int_column(get_null(), 1)

r = if_else(b_t,i_1,i_n)
r = is_null(r)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/false10.csv')

r = if_else(b_t,i_n,i_1)
r = is_null(r)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/true10.csv')

r = if_else(b_n,i_1,i_n)
r = is_null(r)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/true10.csv')

r = if_else(b_n,i_n,i_1)
r = is_null(r)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/false10.csv')