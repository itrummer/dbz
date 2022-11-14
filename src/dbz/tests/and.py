'''
Created on Nov 14, 2022

@author: immanueltrummer
'''
ct = fill_Boolean_column(True, 10)
cf = fill_Boolean_column(False, 10)
cn = fill_Boolean_column(get_null(), 10)

r = logical_and(ct, cf)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/false10.csv')

r = logical_and(ct, ct)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/true10.csv')

r = logical_and(ct, cn)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/null10.csv')

r = logical_and(cf, cn)
t = create_table([r])
write_to_csv(t, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/false10.csv')