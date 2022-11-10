'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
def run_checks(c, nc):
    assert check_column_type(is_null(c))
    assert check_column_type(is_null(nc))
    write_to_csv(c, 'test_output/test.csv')
    assert same_content('test_output/test.csv', 'test_output/false10.csv')
    write_to_csv(nc, 'test_output/test.csv')
    assert same_content('test_output/test.csv', 'test_output/true10.csv')

c = fill_Boolean_column(True, 10)
nc = fill_Boolean_column(get_null(), 10)
run_checks(c, nc)

c = fill_int_column(7, 10)
nc = fill_int_column(get_null(), 10)
run_checks(c, nc)

c = fill_float_column(1.5, 10)
nc = fill_float_column(get_null(), 10)
run_checks(c, nc)

c = fill_string_column('This is a test', 10)
nc = fill_string_column(get_null(), 10)
run_checks(c, nc)