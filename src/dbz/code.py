'''
Created on Mar 10, 2022

@author: immanueltrummer
'''
class Coder():
    """ Translates query plans into code. """
    
    def __init__(self, paths):
        """ Initialize variables and paths. 
        
        Args:
            paths: relevant paths
        """
        self.paths = paths
        self.id_to_plan = {}
    
    def plan_code(self, plan):
        """ Translates plan into code.
        
        Args:
            plan: query plan in JSON
        
        Returns:
            Python code (referencing library operators).
        """
        self.id_to_plan = {}
        lines = []
        for step in plan['rels']:
            lines += [self._step_code(step)]
        return '\n'.join(lines)
    
    def _agg_code(self, agg, groups):
        """ Generates code for processing aggregates.
        
        Args:
            agg: produce code for this aggregate
            groups: column indices for grouping
        
        Returns:
            code processing given aggregate
        """
        kind = agg['agg']['kind']
        name = {'SUM':'Sum', 'AVG':'Avg', 'MIN':'Min', 
                'MAX':'Max', 'COUNT':'Count'}[kind]
        operands = agg['operands']
        params = []
        params += ['table=last_result']
        params += [f'agg_cols={operands}']
        params += [f'group_by_cols={groups}']
        return f'{name}_by_group({",".join(params)})'
    
    def _assignment(self, step, op_code):
        """ Returns code for assigning operation result to variable.
        
        Args:
            step: processing step
            op_code: code for processing operation
        
        Returns:
            code assigning operation result to variable
        """
        result = self._result_name(step['id'])
        return f'{result} = {op_code}\n' +\
            f'last_result = {result}'
    
    def _binary_code(self, operation):
        """ Translates binary operation into code.
        
        Args:
            operation: a binary operation
        
        Returns:
            code realizing the operation
        """
        op_kind = operation['op']['kind']
        op_name = {'PLUS':'addition', 'MINUS':'subtraction', 
                   'TIMES':'multiplication', 'DIVISION':'division',
                   'LESS_THAN_OR_EQUAL':'less_than_or_equal',
                   'LESS_THAN':'less_than',
                   'GREATER_THAN_OR_EQUAL':'greater_than_or_equal',
                   'GREATER_THAN':'greater_than',
                   'EQUAL_TO':'equal'}[op_kind]
        operands = operation['operands']
        left_op = self._operation_code(operands[0])
        right_op = self._operation_code(operands[1])
        return f'{op_name}({left_op},{right_op})'
    
    def _cast_code(self, operation):
        """ Generate code for a casting operation.
        
        Args:
            operation: describes casting operation
        
        Returns:
            code for executing a type cast
        """
        operands = operation['operands']
        assert len(operands) == 1
        operand_code = self._operation_code(operands[0])
        param = f'last_result.get_column({operand_code})'
        new_type = operation['type']['type']
        return f'CAST({param}, {new_type})'
    
    def _column_code(self, column_ref):
        """ Generate code retrieving column of last result. 
        
        Args:
            column_ref: describes column to retrieve from previous result
        
        Returns:
            code retrieving specified column
        """
        column_nr = column_ref['input']
        return f'last_result.get_column({column_nr})'
    
    def _literal_code(self, literal):
        """ Produces a code snippet producing given literal.
        
        Args:
            literal: translate this literal into code
        
        Returns:
            code producing given literal
        """
        return literal['literal']
    
    def _LogicalAggregate(self, step):
        """ Produce code for aggregates (optionally with grouping). 
        
        Args:
            step: plan step representing aggregates
        
        Returns:
            code realizing aggregates
        """
        step_id = step['id']
        result = self._result_name(step_id)
        parts = []
        parts += [f'{result} = Table()']
        aggs = step['aggs']
        groups = step['group']
        for agg in aggs:
            agg_code = self._agg_code(agg, groups)
            add_code = f'{result}.add_column({agg_code})'
            parts += [add_code]
        return '\n'.join(parts)
    
    def _LogicalFilter(self, step):
        """ Produce code for a filter.
        
        Args:
            step: plan step representing filter
        
        Returns:
            code realizing filter
        """
        condition = step['condition']
        pred_code = self._operation_code(condition)
        op_code = f'pick_rows(last_result, {pred_code})'
        return self._assignment(step, op_code)
    
    def _LogicalJoin(self, step):
        """ Produce code for an equality join.
        
        Args:
            step: plan step representing join
        
        Returns:
            code realizing join
        """
        inputs = step['inputs']
        params = [self._result_name(step_id) for step_id in inputs]
        op_code = f'LogicalJoin({",".join(params)})'
        return self._assignment(step, op_code)
    
    def _LogicalProject(self, step):
        """ Produce code for projection.
        
        Args:
            step: plan step representing projection
        
        Returns:
            code realizing projection
        """
        step_id = step['id']
        result = self._result_name(step_id)
        parts = []
        parts += [f'{result} = Table()']
        exprs = step['exprs']
        for expr in exprs:
            expr_code = self._operation_code(expr)
            col_code = f'column = {expr_code}'
            add_code = f'{result}.add_column(column)'
            parts += [col_code]
            parts += [add_code]
        parts += [f'last_result = {result}']
        return '\n'.join(parts)
    
    def _LogicalSort(self, step):
        """ Produces code for a logical sort operation. 
        
        Args:
            step: plan step to translate into code
        
        Returns:
            code for executing plan step
        """
        if 'fetch' in step:
            nr_rows = step['fetch']['literal']
        else:
            nr_rows = -1

        if 'collation' in step:
            collation = step['collation']
            fields = [d['field'] for d in collation]
            flags = [d['direction'] == 'ASCENDING' for d in collation]
        else:
            fields = []
            flags = []
        
        code = f'top_k(last_result, {fields}, {flags}, {nr_rows})'
        return self._assignment(step, code)
    
    def _LogicalTableScan(self, step):
        """ Produces code for table scan.
        
        Args:
            step: plan step representing scan
        
        Returns:
            code realizing scan
        """
        # db = step['table'][0]
        # table = step['table'][1]
        # file_path = f'{self.data_dir}/{db}/{table}'
        table = step['table'][0]
        file_path = f'{self.paths.data_dir}/{table.lower()}.csv'
        scan_code = f'new_table = Table()\nnew_table.from_csv("{file_path}")'
        return scan_code + '\n' + self._assignment(step, 'new_table')
    
    def _operation_code(self, operation):
        """ Generate code realizing given operation. 
        
        Args:
            operation: translate this operation into code
        
        Returns:
            code for realizing operation
        """
        if 'literal' in operation:
            return self._literal_code(operation)
        elif 'input' in operation:
            return self._column_code(operation)
        elif 'op' in operation:
            syntax = operation['op']['syntax']
            name = operation['op']['name']
            if syntax == 'BINARY' or name in ['+', '-']:
                return self._binary_code(operation)
            if name == 'CAST':
                return self._cast_code(operation)
        
        raise ValueError(f'Unhandled operation: {operation}')
    
    def _result_name(self, step_id):
        """ Returns name of intermediate result variable.
        
        Args:
            step_id: return name of variable storing result of this step
        
        Returns:
            name of variable storing intermediate result of step
        """
        return f"result_{step_id}"
    
    def _step_code(self, step):
        """ Translates one plan step into code.
        
        Args:
            step: translate this plan step
        
        Returns:
            code for executing plan step
        """
        rel_op = step['relOp']
        handler = f'_{rel_op}'
        return getattr(self, handler)(step)