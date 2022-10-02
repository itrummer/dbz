def <binary_op>(column_1, column_2):
    """ True where operand_1 <short_op> operand_2.
    
    Args:
        column_1: <Column>.
        column_2: <Column>.
    
    Returns:
        <Column> containing Boolean values, <Null> where any of the operands is <Null>.
    """