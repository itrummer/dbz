'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(1,10)
c2 = fill_int_column(0,10)
t1 = create_table([c1, c2])
t2 = create_table([c1, c2])
r = cross_product(t1, t2)
assert table_cardinality(r) == 100