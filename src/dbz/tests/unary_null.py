'''
Created on Oct 22, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(get_null(), 10)
c2 = fill_int_column(1, 10)
results = []
for c in [c1, c2]:
    r = <SubstituteBy:cast_to_int|cast_to_float|cast_to_string>(c)
    results += [r]

check_null = is_null(results[0])
write_to_csv(check_null, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/true10.csv')

check_not_null = is_null(results[1])
write_to_csv(check_null, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/false10.csv')