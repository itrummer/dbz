def <binary_op>(column_1, column_2):
    """ True where operand_1 <short_op> operand_2.
    
    Args:
        column_1: a column (which <DataInstructions>)
        column_2: a column (which <DataInstructions>)
    
    Returns:
        result column (which <DataInstructions>) of Boolean values, NULL where any of the operands is NULL
    """