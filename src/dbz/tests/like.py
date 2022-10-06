'''
Created on Oct 5, 2022

@author: immanueltrummer
'''
c0 = fill_column(get_null(), 10)
c1 = fill_column('asdfaswtv zaaq2', 10)
c2 = like_expression('%fas_', c0)
c3 = like_expression('%fas_', c1)
c4 = like_expression('%asfdkhjqwetrkj', c1)
last_result = create_table([c0, c1, c2, c3, c4])