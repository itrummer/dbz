'''
Created on Nov 6, 2022

@author: immanueltrummer
'''
n = get_null()
nc = fill_int_column(n, 10)
r = <SubstituteBy:cast_to_Boolean|cast_to_int|cast_to_float|cast_to_string>(nc)
assert check_column_type(r), f'Unexpected type: {type(r)}'