'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
ca = fill_float_column(1.0, 5)
cg = fill_float_column(1.0, 5)
t = create_table([ca, cg])
ag = group_by_<SubstituteBy:max|min|avg>(t,0,[1])
card = table_cardinality(ag)
assert card == 1
ar = get_column(ag, 1)
v = get_value(ar, 0)
assert v == 1.0