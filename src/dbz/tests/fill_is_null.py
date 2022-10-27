n = get_null()
nc = fill_<SubstituteBy:Boolean|int|float|string>_column(n, 10)
nc_is_null = is_null(nc)
for i in range(10):
    assert get_value(nc_is_null, i)