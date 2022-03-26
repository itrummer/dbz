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
        name = {
            'SUM':'sum', 'AVG':'avg', 'MIN':'min', 
            'MAX':'max', 'COUNT':'row_count'}[kind]
        if groups:
            name = 'per_group_' + name
        else:
            name = 'calculate_' + name
        
        operands = agg['operands']
        if not operands:
            operands += [0]
        operands = [f'last_result[{o}]' for o in operands]
        
        params = []
        nr_operands = len(operands)
        if nr_operands == 1:
            params += operands
        elif nr_operands > 1:
            params += [str(operands)]
        if groups:
            params += ['row_id_column']
        
        return f'{name}({",".join(params)})'
    
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
                   'TIMES':'multiplication', 'DIVIDE':'division',
                   'LESS_THAN_OR_EQUAL':'less_than_or_equal',
                   'LESS_THAN':'less_than',
                   'GREATER_THAN_OR_EQUAL':'greater_than_or_equal',
                   'GREATER_THAN':'greater_than',
                   'EQUALS':'equal'}[op_kind]
        operands = operation['operands']
        left_op = self._operation_code(operands[0])
        right_op = self._operation_code(operands[1])
        
        scale_1 = self._get_scale(operands[0])
        scale_2 = self._get_scale(operands[1])
        result_scale = self._get_scale(operation)
        diff_1, diff_2 = self._scale_diffs(
            scale_1, scale_2, result_scale, op_kind)
        left_op = f'multiplication({left_op}, 1e{diff_1})' if diff_1 else left_op
        right_op = f'multiplication({right_op}, 1e{diff_2})' if diff_2 else right_op
        
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
        return f'last_result[{column_nr}]'
    
    def _get_scale(self, node):
        """ Extract scale for exact numeric type results.
        
        Args:
            node: a node in the query plan
        
        Returns:
            scale if node produces exact numeric result, otherwise None
        """
        return node['type'].get('scale', None)
    
    def _literal_code(self, literal):
        """ Produces a code snippet producing given literal.
        
        Args:
            literal: translate this literal into code
        
        Returns:
            code producing given literal
        """
        scale = self._get_scale(literal)
        value = literal['literal']
        if scale is None:
            
            data_type = literal['type']['type']
            if data_type in ['CHAR', 'VARCHAR', 'TEXT']:
                return f"'{value}'"
            else:
                return value
        else:
            return f'round({value}*1e{scale})'
    
    def _LogicalAggregate(self, step):
        """ Produce code for aggregates (optionally with grouping). 
        
        Args:
            step: plan step representing aggregates
        
        Returns:
            code realizing aggregates
        """
        step_id = step['id']
        aggs = step['aggs']
        groups = step['group']
        result = self._result_name(step_id)
        parts = [f'{result} = []']
        
        if groups:
            nr_group_cols = len(groups)
            group_by_cols = [f'last_result[{g}]' for g in groups]
            group_by_list = ', '.join(group_by_cols)
            parts += [f'row_id_rows=to_row_format([{group_by_list}])']
            parts += ['row_id_column=to_tuple_column(row_id_rows)']
            
            parts += ['id_tuples=list(set([tuple(g) for g in row_id_rows]))']
            parts += ['id_rows=[list(t) for t in id_tuples]']
            parts += [f'id_columns=rows_to_columns(id_rows,{nr_group_cols})']
            parts += [f'{result} += id_columns']
            
            parts += ['agg_dicts = []']
            for agg in aggs:
                agg_code = self._agg_code(agg, groups)
                parts += [f'agg_dicts += [{agg_code}]']
            parts += ['agg_rows = []']
            parts += ['for id_tuple in id_tuples:']
            parts += [
                '\tagg_rows += [[agg_dict[id_tuple] ' +\
                'for agg_dict in agg_dicts]]']
            nr_aggs = len(aggs)
            parts += [f'{result} += rows_to_columns(agg_rows,{nr_aggs})']

        else:
        
            for agg in aggs:
                agg_code = self._agg_code(agg, groups)
                add_code = f'{result} += [{agg_code}]'
                parts += [add_code]
        
        parts += [f'last_result = {result}']
        parts += ['last_result = [normalize(c) for c in last_result]']
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
        op_code = f'[filter_column(c, {pred_code}) for c in last_result]'
        return self._assignment(step, op_code)
    
    def _LogicalJoin(self, step):
        """ Produce code for an equality join.
        
        Args:
            step: plan step representing join
        
        Returns:
            code realizing join
        """
        inputs = step['inputs']
        assert(len(inputs) == 2)
        params = [self._result_name(step_id) for step_id in inputs]
        params = [f'to_row_format({p})' for p in params]
        join_pred = step['condition']
        assert(join_pred['op']['kind'] == 'EQUALS')
        col_idx_1 = join_pred['operands'][0]['input']
        col_idx_2_raw = join_pred['operands'][1]['input']
        in_1_name = self._result_name(inputs[0])
        col_idx_2 = f'{col_idx_2_raw}-len({in_1_name})'
        params += [str(col_idx_1), col_idx_2]
        out_fields = step['outputType']['fields']
        nr_out_fields = len(out_fields)
        op_code = f'rows_to_columns(equi_join(' +\
            f'{", ".join(params)}),{nr_out_fields})'
        #op_code = f'rows_to_columns(equi_join({", ".join(params)}),)'
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
        parts += [f'{result} = []']
        exprs = step['exprs']
        for expr in exprs:
            expr_code = self._operation_code(expr)
            col_code = f'column = {expr_code}'
            add_code = f'{result} += [column]'
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
        step_id = step['id']
        result = self._result_name(step_id)
        parts = [f'{result} = to_row_format(last_result)']
        
        if 'collation' in step:
            parts += ['def comparator(row_1, row_2):']
            collation = step['collation']
            for d in collation:
                field_idx = int(d['field'])
                flag = True if d['direction'] == 'ASCENDING' else False
                parts += [f'\tif row_1[{field_idx}] < row_2[{field_idx}]:']
                parts += [f'\t\treturn {-1 if flag else 1}']
                parts += [f'\telif row_1[{field_idx}] > row_2[{field_idx}]:']
                parts += [f'\t\treturn {1 if flag else -1}']
            parts += ['\treturn 0']
            parts += [f'{result} = sort({result}, comparator)']
        
        if 'fetch' in step:
            nr_rows = step['fetch']['literal']
            parts += [f'{result} = {result}[:{nr_rows}]']
        
        out_arity = len(step['outputType']['fields'])
        parts += [f'{result} = rows_to_columns({result},{out_arity})']
        parts += [f'last_result = {result}']
        return '\n'.join(parts)

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
        scan_code = f'new_table = load_from_csv("{file_path}")\n' +\
            'new_table = to_columnar_format(new_table)'
        return scan_code + '\n' + self._assignment(step, 'new_table')
    
    def _nary_boolean_code(self, operation):
        """ Generate code realizing n-ary Boolean operator.
        
        Args:
            operation: translate this operation into code
        
        Returns:
            code realizing operation
        """
        op_kind = operation['op']['kind']
        op_name = {'AND':'logical_and', 'OR':'logical_or'}[op_kind]
        operands = operation['operands']
        params = [self._operation_code(operand) for operand in operands]
        return f'{op_name}([{", ".join(params)}])'
    
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
            if name in ['AND', 'OR']:
                return self._nary_boolean_code(operation)
            if syntax == 'BINARY' or name in ['+', '-']:
                return self._binary_code(operation)
            if name == 'CAST':
                return self._cast_code(operation)
            if name == 'NOT':
                return self._unary_code(operation)
        
        raise ValueError(f'Unhandled operation: {operation}')
    
    def _result_name(self, step_id):
        """ Returns name of intermediate result variable.
        
        Args:
            step_id: return name of variable storing result of this step
        
        Returns:
            name of variable storing intermediate result of step
        """
        return f"result_{step_id}"
    
    def _scale_diffs(self, scale_1, scale_2, result_scale, op_kind):
        """ Calculate required (re)scaling for inputs to binary operation.
        
        Args:
            scale_1: scale of first (left) input
            scale_2: scale of second (right) input
            result_scale: scale of operation result
            op_kind: kind of operation
        
        Returns:
            two values indicating by how much to scale left and right input
        """
        if scale_1 is None and scale_2 is None:
            return 0, 0
        elif scale_1 is None and scale_2 is not None:
            return 0, -scale_2
        elif scale_1 is not None and scale_2 is None:
            return -scale_1, 0
        elif op_kind in ['LESS_THAN_OR_EQUAL', 'LESS_THAN', 
                         'GREATER_THAN_OR_EQUAL',
                         'GREATER_THAN', 'EQUALS',
                         'PLUS', 'MINUS']:
            if scale_1 < scale_2:
                return scale_2 - scale_1, 0
            else:
                return 0, scale_1 - scale_2
        elif op_kind == 'TIMES':
            return 0, 0
        elif op_kind == 'DIVIDE':
            return result_scale - scale_1, 0
        else:
            raise NotImplementedError(f'Unknown scaling scenario!')
    
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
    
    def _unary_code(self, operation):
        """ Translates unary operation into code.
        
        Args:
            operation: write code for this operation
        
        Returns:
            code processing input operation
        """
        operands = operation['operands']
        assert len(operands) == 1
        operand_code = self._operation_code(operands[0])
        kind = operation['op']['kind']
        op_name = {'NOT':'logical_not'}[kind]
        return f'{op_name}({operand_code})'
    
    def _unscale_code(self, node, code):
        """ Returns code to transform scaled into unscaled representation. 
        
        Args:
            node: a node in the query plan tree
            code: code for evaluating node
        
        Returns:
            code for unscaling result of given code
        """
        scale = self._get_scale(node)
        if scale is None:
            return code
        else:
            return f'division({code},1e{scale})'