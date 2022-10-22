'''
Created on Oct 22, 2022

@author: immanueltrummer
'''
c1 = fill_column(get_null(), 10)
c2 = fill_column(1, 10)
cmp = <SubstituteBy:greater_than|less_than>(c1, c2)
r = is_null(cmp)
for i in range(10):
    assert get_value(r, i)