'''
Created on Nov 8, 2022

@author: immanueltrummer
'''
import filecmp

c = fill_int_column(1, 10)
t = create_table([c, c])
write_to_csv(t, 'dummy.csv')
assert filecmp.cmp('dummy.csv', 'test_output/store.csv')