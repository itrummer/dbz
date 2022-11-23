def cross_product(table_1, table_2):
    """ Performs a cross product between tables.

    - Iterate over all rows from table_1:
      - Iterate over all rows from table_2:
        - Concatenate rows and add to result.
    - Transform into <Table>.<TablePost>

    Args:
        table_1: <Table>.
        table_2: <Table>.

    Returns:
        <Table>.
    """