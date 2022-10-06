'''
Created on Oct 5, 2022

@author: immanueltrummer
'''
c0 = fill_column(get_null(), 10)
c1 = fill_column(1, 10)
c2 = fill_column(2, 10)
c3 = fill_column(3, 10)
c4 = multiplication(c1, c2)
c5 = multiplication(c3, c4)
c6 = multiplication(c5, c0)
last_result = create_table([c1, c2, c3, c4, c5, c6])