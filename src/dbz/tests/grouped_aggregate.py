'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
ca = fill_float_column(1.5, 5)
cg = fill_float_column(1.5, 5)
t = create_table([ca, cg])
ag = group_by_<SubstituteBy:max|min|avg>(t,0,[1])
write_to_csv(ag, 'test_output/test.csv')
same_content('test_output/test.csv', 'test_output/float1.5-1.5_1.csv')