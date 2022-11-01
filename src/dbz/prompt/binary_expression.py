def <binary_op>(column_1, column_2):
    """ Performs <binary_op> between two columns.
    
    1. Rows with <Null> in column_1 or column_2 map to <Null>.
    2. Element-wise <binary_op> of column_1 and column_2.

    Args:
        operand_1: <Column>.
        operand_2: <Column>.

    Returns:
        <Column>.
    """