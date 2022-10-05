'''
Created on Oct 4, 2022

@author: immanueltrummer
'''
c = fill_column(1, 5)
map(c, lambda x:x+1)
c2 = fill_column(2, 5)
map(c2, lambda x:x+10)
last_result = create_table([c, c2])