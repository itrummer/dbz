'''
Created on Oct 5, 2022

@author: immanueltrummer
'''
c0 = fill_column(get_null(), 10)
c1 = fill_column(1.0, 10)
c2 = fill_column(2.0, 10)
c3 = fill_column(3.0, 10)
c4 = division(c1, c2)
c5 = division(c3, c4)
c6 = division(c5, c0)
last_result = create_table([c1, c2, c3, c4, c5, c6])