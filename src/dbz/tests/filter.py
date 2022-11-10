'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
c1 = fill_string_column('This is a test', 10)
tc = fill_Boolean_column(True, 10)
fc = fill_Boolean_column(False, 10)

table = create_table([c1])
f1 = filter_table(table, tc)
write_to_csv(f1, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/string10.csv')

f2 = filter_table(table, fc)
write_to_csv(f2, 'test_output/test.csv')
assert same_content('test_output/test.csv', 'test_output/empty.csv')