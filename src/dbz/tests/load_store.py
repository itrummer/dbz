'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
t = load_from_csv('test_input/test1.csv')
assert check_table_type(t), f'Unexpected type: {type(t)}'
write_to_csv(t, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_input/test1.csv')