'''
Created on Nov 17, 2022

@author: immanueltrummer
'''
src = load_from_csv('test_input/test2.csv')
c = get_column(src, 0)
n = is_null(c)
out = create_table([n])
write_to_csv(out, 'test_output/test2_is_null.csv')