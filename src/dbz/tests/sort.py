'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(1, 10)
c2 = fill_int_column(1, 10)
c3 = fill_int_column(get_null(), 10)
table = create_table([c1, c2, c3])
key_columns = [0,2]
sorted_table = sort_rows(table, key_columns)