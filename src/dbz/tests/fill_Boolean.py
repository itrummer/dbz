'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
tc = fill_Boolean_column(True, 10)
tt = create_table([tc])
write_to_csv(tt, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/true10.csv')

fc = fill_Boolean_column(False, 10)
ft = create_table([fc])
write_to_csv(ft, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/false10.csv')