'''
Created on Nov 14, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(1, 10)
t1 = create_table([c1])

c2 = fill_string_column('This is a test', 10)
t2 = set_column(t1, 0, c2)

write_to_csv(t2, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/string10.csv')