'''
Created on Oct 30, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(1,10)
c2 = fill_int_column(0,10)
t1 = create_table([c1, c2])
t2 = create_table([c1, c2])
r = full_outer_join(t1, t2, [1], [1])
assert table_cardinality(r) == 100
r = full_outer_join(t1, t2, [0], [0])
assert table_cardinality(r) == 100
r = full_outer_join(t1, t2, [1], [0])
assert table_cardinality(r) == 20
r = full_outer_join(t1, t2, [0], [1])
assert table_cardinality(r) == 20