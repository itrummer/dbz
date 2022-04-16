def <binary_op>(column_1, column_2):
    """ Performs <binary_op> between two columns.
    
    Args:
        operand_1: a column (which <DataInstructions>)
        operand_2: a column (which <DataInstructions>)
    
    Returns:
        result column (which <DataInstructions>), NULL where any of the operands is NULL
    """