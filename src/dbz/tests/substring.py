'''
Created on Oct 5, 2022

@author: immanueltrummer
'''
c0 = fill_column(get_null(), 12)
c1 = fill_column('Testasdfasdfa', 12)
c2 = substring(c0, 2, 7)
c3 = substring(c1, 2, 7)
last_result = create_table([c0, c1, c2, c3])