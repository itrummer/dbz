'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c = fill_int_column(1, 10)
t = create_table([c, c])
a = group_by_sum(t, 0, [1])
card = table_cardinality(a) 
assert card == 1, card
r = get_column(a, 1)
v = get_value(r, 0)
assert v == 10, v