'''
Created on Oct 22, 2022

@author: immanueltrummer
'''
c1 = fill_column(get_null(), 10)
c2 = fill_column('1', 10)
results = []
for c in [c1, c2]:
    r = <SubstituteBy:cast_to_int|cast_to_float|cast_to_string>(c)
    results += [r]

check_null = is_null(results[0])
check_not_null = is_null(results[1])
for i in range(10):
    assert get_value(check_null, i)
    assert not get_value(check_not_null, i)