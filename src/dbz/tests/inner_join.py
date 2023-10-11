'''
Created on Oct 27, 2022

@author: immanueltrummer
'''
c1 = fill_int_column(1,10)
c2 = fill_int_column(0,10)
t1 = create_table([c1, c2])
t2 = create_table([c1, c2])

r = equality_join(t1, t2, [1], [1])
write_to_csv(r, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/1010_100.csv')

r = equality_join(t1, t2, [0], [0])
write_to_csv(r, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/1010_100.csv')

r = equality_join(t1, t2, [1], [0])
write_to_csv(r, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/empty.csv')

r = equality_join(t1, t2, [0], [1])
write_to_csv(r, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/empty.csv')

r = equality_join(t1, t2, [1], [1])
r = equality_join(r, t2, [1], [1])
write_to_csv(r, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/101010_1000.csv')