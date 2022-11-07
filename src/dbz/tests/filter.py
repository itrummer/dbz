'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c1 = fill_string_column('test', 10)
tc = fill_Boolean_column(True, 10)
fc = fill_Boolean_column(False, 10)

table = create_table([c1])
f1 = filter_table(table, tc)
assert table_cardinality(f1) == 10
f2 = filter_table(table, fc)
assert table_cardinality(f2) == 0