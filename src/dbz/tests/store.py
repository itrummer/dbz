'''
Created on Nov 8, 2022

@author: immanueltrummer
'''
c = fill_int_column(1, 10)
t = create_table([c, c])
write_to_csv(t, 'dummy.csv')