'''
Created on Oct 5, 2022

@author: immanueltrummer
'''
c1 = fill_column(get_null(), 10)
c2 = map_column(c1, lambda x:x+1)
last_result = create_table([c1, c2])