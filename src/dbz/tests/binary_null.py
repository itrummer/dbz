'''
Created on Oct 22, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(get_null(), 10)
c2 = fill_int_column(1, 10)

results = []
for in_1, in_2 in [(c1,c2), (c2,c1), (c1,c1), (c2,c2)]:
    cmp = <SubstituteBy:greater_than|less_than|equal|not_equal|less_than_or_equal|greater_than_or_equal|addition|subtraction|multiplication|division>(in_1, in_2)
    r = is_null(cmp)
    results += [r]

for i in [0, 1, 2]:
    r = results[i]
    for j in range(10):
        assert get_value(r, j)

for i in [3]:
    r = results[i]
    for j in range(10):
        assert not get_value(r, j)