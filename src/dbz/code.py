'''
Created on Mar 10, 2022

@author: immanueltrummer
'''
import dbz.util

class Coder():
    """ Translates query plans into code. """
    
    def __init__(self, paths, print_results):
        """ Initialize variables and paths. 
        
        Args:
            paths: relevant paths
            print_results: print out samples from intermediate results?
        """
        self.paths = paths
        self.id_to_plan = {}
        self.print_results = print_results
    
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
        
        final_step = plan['rels'][-1]
        lines += [self._post_code(final_step)]

        return '\n'.join(lines)
    
    def _agg_code(self, agg, groups):
        """ Generates code for processing aggregates.
        
        Args:
            agg: produce code for this aggregate
            groups: column indices for grouping
        
        Returns:
            code processing given aggregate
        """
        operands = agg['operands']
        distinct = agg['distinct']
        kind = agg['agg']['kind']
        row_id_column = 'row_id_column' if groups else 'None'
        
        parts = []
        parts += [
            f'params = prepare_aggregate(' +\
            f'input_rel,{str(operands)},' +\
            f'{row_id_column},{distinct})']
        
        name = {
            'SUM':'sum', 'AVG':'avg', 'MIN':'min', 
            'MAX':'max', 'COUNT':'row_count'}[kind]
        if groups:
            name = 'per_group_' + name
        else:
            name = 'calculate_' + name
        parts += [f'agg_result = {name}(*params)']

        return '\n'.join(parts)
    
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
                   'EQUALS':'equal', 'NOT_EQUALS':'not_equal'}[op_kind]
        operands = operation['operands']
        left_op = self._operation_code(operands[0])
        right_op = self._operation_code(operands[1])
        op_types = [op['type']['type'] for op in operands]
        
        if all(t in ['DECIMAL', 'NUMERIC', 'FLOAT', 'INTEGER'] for t in op_types):
            scale_1 = self._get_scale(operands[0])
            scale_2 = self._get_scale(operands[1])
            result_scale = self._get_scale(operation)
            diff_1, diff_2 = self._scale_diffs(
                scale_1, scale_2, result_scale, op_kind)
            left_op = f'multiplication({left_op}, 1e{diff_1})' if diff_1 else left_op
            right_op = f'multiplication({right_op}, 1e{diff_2})' if diff_2 else right_op
        
        elif all(t in ['CHAR', 'VARCHAR'] for t in op_types):
            precision_1 = self._get_precision(operands[0])
            precision_2 = self._get_precision(operands[1])
            precision_1 = 0 if precision_1 is None else precision_1
            precision_2 = 0 if precision_2 is None else precision_2
            if not (precision_1 == precision_2):
                pad_to = max(precision_1, precision_2)
                left_op = f'smart_padding({left_op}, {pad_to})'
                right_op = f'smart_padding({right_op},{pad_to})'
        
        elif all(t in ['DATE'] for t in op_types):
            pass
        
        else:
            raise NotImplementedError(
                f'Unsupported types for binary operation: {op_types}; ' +\
                    f'operation: {operation}')
        
        return f'{op_name}(*fix_rel([{left_op},{right_op}]))'
    
    def _case_code(self, operation):
        """ Generate code representing case statement.
        
        Args:
            operation: describes case statement
        
        Returns:
            code realizing case statement
        """
        operands = operation['operands']
        op_codes = [self._operation_code(op) for op in operands]
        pred_code, if_code, else_code = op_codes
        return f'if_else(*fix_rel([{pred_code},{if_code},{else_code}]))'
    
    def _cast_code(self, operation):
        """ Generate code for a casting operation.
        
        Args:
            operation: describes casting operation
        
        Returns:
            code for executing a type cast
        """
        operands = operation['operands']
        assert len(operands) == 1
        operand = operands[0]
        operand_code = self._operation_code(operand)
        
        old_type = {k:v for k, v in operand['type'].items() if k != 'nullable'}
        new_type = {k:v for k, v in operation['type'].items() if k != 'nullable'}
        if old_type == new_type:
            return operand_code
        
        scale_before = self._get_scale(operand)
        scale_after = self._get_scale(operation)
        scale_before = 0 if scale_before is None else scale_before
        scale_after = 0 if scale_after is None else scale_after
        if not (scale_before == scale_after):
            diff = scale_after - scale_before
            operand_code = f'multiplication({operand_code},1e{diff})'
        
        old_type_name = old_type['type'].lower()
        new_type_name = new_type['type'].lower()
        if new_type_name == 'integer':
            # TODO: needs to be cleaned up
            return f'map_column({operand_code}, lambda r:round(r+1e-10))'
        elif old_type_name == 'char' and new_type_name == 'char':
            pad_to = new_type['precision']
            return f'smart_padding({operand_code},{pad_to})'
        else:
            return f'cast_to_{new_type_name}({operand_code})'
    
    def _column_code(self, column_ref):
        """ Generate code retrieving column of last result. 
        
        Args:
            column_ref: describes column to retrieve from previous result
        
        Returns:
            code retrieving specified column
        """
        column_nr = column_ref['input']
        return f'input_rel[{column_nr}]'
    
    def _extract_code(self, operation):
        """ Generates code for extracting elements of a date.
        
        Args:
            operation: describes extraction operation
        
        Returns:
            code performing extraction
        """
        source = operation['operands'][1]
        assert(source['type']['type'] == 'DATE')
        source_code = self._operation_code(source)
        field = operation['operands'][0]['literal'].lower()
        assert field in ['year', 'month', 'day'], \
            f'Unsupported extraction: {field}'
        return f'smart_date_extract({source_code},"{field}")'
    
    def _get_precision(self, node):
        """ Extract precision for chars and numeric nodes.
        
        Args:
            node: an expression node
        
        Returns:
            precision or None (if not specified)
        """
        return node['type'].get('precision', None)
    
    def _get_scale(self, node):
        """ Extract scale for exact numeric type results.
        
        Args:
            node: a node in the query plan
        
        Returns:
            scale if node produces exact numeric result, otherwise None
        """
        return node['type'].get('scale', None)
    
    def _like_code(self, node):
        """ Generate code for evaluating LIKE expression.
        
        Args:
            node: describes LIKE expression
        
        Returns:
            code for evaluating LIKE expression
        """
        operands = node['operands']
        to_test = self._operation_code(operands[0])
        like_expr = self._operation_code(operands[1])
        pred_code = f'lambda s:re.match({like_expr}.replace(\'%\', \'.*\'), s) is not None'
        return f'map_column({to_test}, {pred_code})'
    
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
                value = f"None if {value} is None else '{value}'"
        else:
            value = f'None if {value} is None else round({value}*1e{scale})'
        return f'fill_column({value},1)'
    
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
        
        parts = ['']
        parts += [f'# LogicalAggregate: aggs: {aggs}; groups {groups}']
        parts += [f'{result} = []']
        
        grouping = True if groups else False
        if grouping:
            nr_group_cols = len(groups)
            group_by_cols = [f'input_rel[{g}]' for g in groups]
            group_by_list = ', '.join(group_by_cols)
            parts += [f'row_id_rows=to_row_format([{group_by_list}])']
            parts += ['row_id_column=to_tuple_column(row_id_rows)']
            
            parts += ['id_tuples=list(set([tuple(g) for g in row_id_rows]))']
            parts += ['id_rows=[list(t) for t in id_tuples]']
            parts += [f'id_columns=rows_to_columns(id_rows,{nr_group_cols})']
            parts += [f'{result} += id_columns']
            
            parts += ['agg_dicts_defs = []']
            for agg in aggs:
                parts += [self._agg_code(agg, groups)]
                def_val = 0 if agg['agg']['kind'] == 'COUNT' else None
                parts += [f'agg_dicts_defs += [(agg_result,{def_val})]']
            parts += ['agg_rows = []']
            parts += ['for id_tuple in id_tuples:']
            parts += [
                '\tagg_rows += [' +\
                '[dict_def[0].get(id_tuple, dict_def[1]) ' +\
                'for dict_def in agg_dicts_defs]]']
            nr_aggs = len(aggs)
            parts += [f'{result} += rows_to_columns(agg_rows,{nr_aggs})']

        else:
        
            for agg in aggs:
                parts += [f'if input_rel and nr_rows(input_rel[0]):']
                parts += ['\t' + self._agg_code(agg, groups)]
                parts += ['else:']
                def_val = 0 if agg['agg']['kind'] == 'COUNT' else None
                parts += [f'\tagg_result = {def_val}']
                parts += [f'{result} += [agg_result]']
        
        parts += [f'{result} = adjust_after_aggregate({result}, {grouping})']
        parts += [f'last_result = {result}']
        return '\n'.join(parts)
    
    def _LogicalFilter(self, step):
        """ Produce code for a filter.
        
        Args:
            step: plan step representing filter
        
        Returns:
            code realizing filter
        """
        result = self._result_name(step['id'])
        condition = step['condition']
        pred_code = self._operation_code(condition)
        parts = [f'p_idx = {pred_code}']
        parts += [f'{result} = [filter_column(c, p_idx) for c in input_rel]']
        return '\n'.join(parts)
    
    def _LogicalJoin(self, step):
        """ Produce code for an equality join.
        
        Args:
            step: plan step representing join
        
        Returns:
            code realizing join
        """
        inputs = step['inputs']
        assert(len(inputs) == 2)
        operands = [self._result_name(step_id) for step_id in inputs]
        step_id = step['id']
        result = self._result_name(step_id)
        
        params = operands
        params = [f'to_row_format({p})' for p in params]
        join_pred = step['condition']
        conjuncts = dbz.util.get_conjuncts(join_pred)
        
        def is_eq_col_pred(pred):
            """ Returns true iff equality between two columns. """
            if pred['op']['kind'] == 'EQUALS' and \
                all('input' in op for op in pred['operands']):
                return True
            else:
                return False

        eq_cols = []
        join_preds = [c for c in conjuncts if is_eq_col_pred(c)]
        for join_pred in join_preds:
            col_idxs = [op['input'] for op in join_pred['operands']]
            col_idx_1 = min(col_idxs)
            col_idx_2_raw = max(col_idxs)
            in_1_name = self._result_name(inputs[0])
            col_idx_2 = f'{col_idx_2_raw}-len({in_1_name})'
            eq_cols += [f'({col_idx_1},{col_idx_2})']

        params += [f'[{", ".join(eq_cols)}]']
        op_code = f'equi_join({", ".join(params)})'
        
        parts = []
        parts += [f'{result} = {op_code}']
        nr_out_cols = len(step['outputType']['fields'])
        join_type = step['joinType']
        if join_type in ['left', 'full']:
            parts += [
                f'{result} = {result} + ' +\
                f'complete_outer(to_row_format(' +\
                f'{operands[0]}),0,{nr_out_cols},{result})']
        if join_type in ['right', 'full']:
            parts += [
                f'{result} = {result} + ' +\
                f'complete_outer(to_row_format(' +\
                f'{operands[1]}),1,{nr_out_cols},{result})']
        parts += [f'{result} = rows_to_columns({result},{nr_out_cols})']
        
        filter_preds = [c for c in conjuncts if not is_eq_col_pred(c)]
        if filter_preds:
            parts += [f'input_rel = {result}']
            filter_codes = []
            for filter_pred in filter_preds:
                filter_code = self._operation_code(filter_pred)
                filter_codes += [filter_code]
            parts += [f'p_idx = smart_logical_and([{", ".join(filter_codes)}])']
            parts += [f'{result} = [filter_column(c,p_idx) for c in {result}]']
        
        return '\n'.join(parts)
    
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
        parts += [f'{result} = adjust_after_project(input_rel, {result})']
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
        parts = [f'{result} = to_row_format(input_rel)']
        
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
    
    def _LogicalValues(self, step):
        """ Uses rows specified as part of the query.
        
        Args:
            step: plan step specifying tuples
        
        Returns:
            code generating given tuples
        """
        result = self._result_name(step['id'])
        nr_columns = len(step['type'])
        in_rows = step['tuples']
        out_rows = []
        for in_row in in_rows:
            out_row = []
            for in_field in in_row:
                out_field = self._literal_code(in_field)
                out_row += [out_field]
            out_rows += [out_row]
        
        parts = []
        parts += [f'out_rows = {str(out_rows)}']
        parts += [f'{result} = rows_to_columns(out_rows, {nr_columns})']
        return '\n'.join(parts)
    
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
        return f'{op_name}(*fix_rel([{", ".join(params)}]))'
    
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
            if name == 'CASE':
                return self._case_code(operation)
            if name == 'CAST':
                return self._cast_code(operation)
            if name == 'EXTRACT':
                return self._extract_code(operation)
            if name in [
                'NOT', 'IS NULL', 'IS NOT NULL', 
                'IS TRUE', 'IS NOT TRUE', 
                'IS FALSE', 'IS NOT FALSE']:
                return self._unary_code(operation)
            if name == 'LIKE':
                return self._like_code(operation)
            if name == 'SUBSTRING':
                return self._substring_code(operation)
        
        raise ValueError(f'Unhandled operation: {operation}')
    
    def _post_code(self, final_step):
        """ Code for column-type specific post-processing. 
        
        Args:
            final_step: final step in query plan
        
        Returns:
            code for post-processing final result
        """
        #parts = ['last_result = [normalize(c) for c in last_result]']
        parts = []
        parts += ['last_result = to_row_format(last_result)']
        parts += ['last_result = [list(r) for r in last_result]']
        col_types = final_step['outputType']['fields']
        for col_idx, col_type in enumerate(col_types):
            base_type = col_type['type']
            if base_type in ['DECIMAL', 'NUMERIC']:
                if 'scale' in col_type:
                    scale = col_type['scale']
                    parts += ['for row in last_result:']
                    parts += [f'\trow[{col_idx}] *= 1e-{scale}']
            elif base_type in ['CHAR']:
                length = col_type['precision']
                parts += ['for row in last_result:']
                parts += [f'\trow[{col_idx}] = row[{col_idx}].ljust({length})']
            elif base_type in ['DATE']:
                parts += ['from datetime import date, timedelta']
                parts += ["ref_date = date(1970,1,1)"]
                parts += ['for row in last_result:']
                parts += [f'\tdate_diff = timedelta(days=row[{col_idx}])']
                parts += [f'\tnew_date = ref_date + date_diff']
                parts += [f'\trow[{col_idx}] = str(new_date)']
        return '\n'.join(parts)
    
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
        scale_1 = 0 if scale_1 is None else scale_1
        scale_2 = 0 if scale_2 is None else scale_2
        result_scale = 0 if result_scale is None else result_scale
        if op_kind in ['PLUS', 'MINUS']:
            return result_scale - scale_1, result_scale - scale_2
        elif op_kind == 'TIMES':
            if scale_1 < scale_2:
                return result_scale - scale_1 - scale_2, 0
            else:
                return 0, result_scale - scale_1 - scale_2
        elif op_kind == 'DIVIDE':
            return result_scale - scale_1 + scale_2, 0
        elif op_kind in ['LESS_THAN_OR_EQUAL', 'LESS_THAN', 
                         'GREATER_THAN_OR_EQUAL', 'GREATER_THAN', 
                         'EQUALS', 'NOT_EQUALS']:
            if scale_1 < scale_2:
                return scale_2 - scale_1, 0
            else:
                return 0, scale_1 - scale_2
        else:
            raise NotImplementedError(f'Scaling {op_kind} not implemented!')
    
    def _step_code(self, step):
        """ Translates one plan step into code.
        
        Args:
            step: translate this plan step
        
        Returns:
            code for executing plan step
        """
        op_id = step['id']
        rel_op = step['relOp']
        parts = []
        parts += [f'# Operation ID: {op_id}; Operator: {rel_op}']
        inputs = [self._result_name(in_) for in_ in step['inputs']] + ['[]']
        if len(inputs) == 2:
            parts += [f'input_rel = ' + ' + '.join(inputs)]
        handler = f'_{rel_op}'
        parts += [getattr(self, handler)(step)]
        result = self._result_name(op_id)
        # parts += [f'{result}=[normalize(c) for c in {result}]']
        parts += [f'last_result = {result}']
        if self.print_results:
            parts += [f'print(f"Column sizes in {result}: ' +\
                      f'{{[nr_rows(c) for c in {result}]}}")']
            parts += [f'print(f"Sample from {result}:")']
            parts += [f'r = nr_rows({result}[0]) if {result} else 0']
            parts += [f'print([c[:min(r,10)] for c in {result}])']
        return '\n'.join(parts)
    
    def _substring_code(self, operation):
        """ Generates code for extracting substrings.
        
        Args:
            operation: describes substring extraction
        
        Returns:
            code for extracting substrings
        """
        operands = operation['operands']
        op_codes = [self._operation_code(op) for op in operands]
        src, start, length = op_codes
        return f'smart_substring({src},{start},{length})'
    
    def _unary_code(self, operation):
        """ Translates unary operation into code.
        
        Args:
            operation: write code for this operation
        
        Returns:
            code processing input operation
        """
        operands = operation['operands']
        assert len(operands) == 1
        op_code = self._operation_code(operands[0])
        kind = operation['op']['kind']
        if kind in ['IS_NULL', 'IS_NOT_NULL']:
            op_code = f'smart_is_null({op_code})'
        elif kind in ['IS_TRUE', 'IS_NOT_TRUE']:
            op_code = f'logical_and([' +\
                f'logical_not(is_null({op_code})),' +\
                    f'{op_code}])'
        if kind in ['IS_FALSE', 'IS_NOT_FALSE']:
            op_code = f'logical_and([' +\
                f'logical_not(is_null({op_code})),' +\
                    f'logical_not({op_code})])'
        if 'NOT' in kind:
            return f'logical_not({op_code})'
        else:
            return op_code