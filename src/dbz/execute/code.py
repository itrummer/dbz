'''
Created on Mar 10, 2022

@author: immanueltrummer
'''
import dbz.util
import pandas as pd

class Coder():
    """ Translates query plans into code. """
    
    def __init__(self, paths, print_results):
        """ Initialize variables and paths. 
        
        Args:
            paths: relevant paths
            print_results: print out samples from intermediate results?
        """
        self.paths = paths
        self.id_to_step = {}
        self.print_results = print_results
        self.id2like = {}
    
    def plan_code(self, plan):
        """ Translates plan into code.
        
        Args:
            plan: query plan in JSON
        
        Returns:
            Python code (referencing library operators).
        """
        self.id_to_step = {}
        for step in plan['rels']:
            step_id = step['id']
            self.id_to_step[step_id] = step
        
        self.id2like = {}
        step_lines = []
        for step in plan['rels']:
            step_lines += [self._step_code(step)]
        
        final_step = plan['rels'][-1]
        step_lines += [self._post_code(final_step)]
        
        compilation_lines = []
        for like_id, like_pattern in self.id2like.items():
            line = f'pattern{like_id} = re.compile("{like_pattern}")'
            compilation_lines += [line]

        return '\n'.join(compilation_lines + step_lines)

    def _assignment(self, step, op_code):
        """ Returns code for assigning operation result to variable.
        
        Args:
            step: processing step
            op_code: code for processing operation
        
        Returns:
            code assigning operation result to variable
        """
        result = self._result_name(step['id'])
        return f'{result} = {op_code}'
    
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
        
        if all(t in [
            'DECIMAL', 'NUMERIC', 'FLOAT', 
            'DOUBLE', 'INTEGER'] for t in op_types):
            scale_1 = self._get_scale(operands[0])
            scale_2 = self._get_scale(operands[1])
            result_scale = self._get_scale(operation)
            diff_1, diff_2 = self._scale_diffs(
                scale_1, scale_2, result_scale, op_kind)
            left_op = f'multiply_by_scalar({left_op}, 1e{diff_1})' if diff_1 else left_op
            right_op = f'multiply_by_scalar({right_op}, 1e{diff_2})' if diff_2 else right_op
        
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
        
        op_internal_types = [self._internal_type(t) for t in op_types]
        # result_sql_type = operation['type']['type']
        # result_internal_type = self._internal_type(result_sql_type)
        # return f'fix_nulls(' +\
            # f'scale_columns([{left_op},{right_op}], {op_internal_types}),' +\
            # f'{op_name}(*' +\
            # f'scale_columns([{left_op},{right_op}], {op_internal_types})),' +\
            # f'"{result_internal_type}")'
        return f'{op_name}(*scale_columns(' +\
            f'[{left_op},{right_op}], {op_internal_types}))'
    
    def _case_code(self, operation):
        """ Generate code representing case statement.
        
        Args:
            operation: describes case statement
        
        Returns:
            code realizing case statement
        """
        operands = operation['operands']
        op_codes = [self._operation_code(op) for op in operands]
        op_sql_types = [op['type']['type'] for op in operands]
        op_internal_types = [self._internal_type(t) for t in op_sql_types]
        pred_code, if_code, else_code = op_codes
        return f'if_else(*scale_columns(' +\
            f'[{pred_code},{if_code},{else_code}], ' +\
            f'{op_internal_types}))'
    
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
        
        old_type_name = old_type['type'].lower()
        new_type_name = new_type['type'].lower()
        scale_before = self._get_scale(operand)
        scale_after = self._get_scale(operation)
        scale_before = 0 if scale_before is None else scale_before
        scale_after = 0 if scale_after is None else scale_after
        if not (scale_before == scale_after):
            diff = scale_after - scale_before
            if diff > 0:
                operand_code = f'multiply_by_scalar({operand_code},1e{diff})'
            else:
                operand_code = f'divide_by_scalar({operand_code},1e{-diff})'
            # if new_type_name in ['varchar', 'float'] and diff < 0:
                # operand_code = f'map_column({operand_code},' +\
                    # f'lambda i:round(i,-{diff}))'
        
        if old_type_name == 'char' and new_type_name == 'char':
            pad_to = new_type['precision']
            return f'smart_padding({operand_code},{pad_to})'
        elif new_type_name == 'varchar':
            return f'cast_to_string({operand_code})'
        else:
            new_internal_type = self._internal_type(new_type_name)
            suffix = '_round' if new_internal_type == 'int' else ''
            return f'cast_to_{new_internal_type}{suffix}({operand_code})'
    
    def _column_code(self, column_ref):
        """ Generate code retrieving column of last result. 
        
        Args:
            column_ref: describes column to retrieve from previous result
        
        Returns:
            code retrieving specified column
        """
        column_nr = column_ref['input']
        return f'get_column(in_rel_1,{column_nr})'
    
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
    
    def _get_arity(self, step):
        """ Get number of columns in step output. 
        
        Args:
            step: processing step in plan
        
        Returns:
            number of output columns
        """
        return len(step['outputType']['fields'])
    
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
    
    def _grouped_aggs_code(self, step):
        """ Generate code for processing grouped aggregates. 
        
        Args:
            step: processing step representing grouped aggregates
        
        Returns:
            code for processing aggregates with grouping
        """
        step_id = step['id']
        aggs = step['aggs']
        groups = step['group']
        result = self._result_name(step_id)
        
        parts = [f'# LogicalAggregate: aggs: {aggs}; groups {groups}']
        if not aggs:
            aggs = [{'distinct':False, 'agg':{'kind':'COUNT'}, 'operands':[]}]
        
        nr_group_cols = len(groups)
        result_idx = nr_group_cols
        for agg_idx, agg in enumerate(aggs):
            distinct = agg['distinct']
            kind = agg['agg']['kind']
            if kind == 'SINGLE_VALUE':
                kind = 'MIN'
            operands = agg['operands']
            if kind in ['SUM', 'AVG', 'MIN', 'MAX']:
                assert len(operands) == 1
                operand = operands[0]
                fct_name = f'group_by_{kind.lower()}'
                params = f'in_rel_1, {operand}, {str(groups)}'
                parts += [f'agg_tbl = {fct_name}({params})']
            else:
                assert kind == 'COUNT'
                params = f'in_rel_1, {str(groups)}, {str(operands)}, {distinct}'
                parts += [f'agg_tbl = grouped_count({params})']

            params = f'agg_tbl, list(range({nr_group_cols}))'
            parts += [f'agg_tbl = sort_rows({params})']
            if not agg_idx:
                parts += ['result_cols = [get_column(agg_tbl, i)' +\
                          f' for i in range({result_idx})]']

            parts += [f'result_col = get_column(agg_tbl, {result_idx})']
            parts += ['result_cols += [result_col]']
        
        parts += [f'{result} = create_table(result_cols)']
        return '\n'.join(parts)
    
    def _internal_type(self, sql_type):
        """ Returns internal type representing given SQL type.
        
        Args:
            sql_type: SQL type in string representation
        
        Returns:
            corresponding internal type (in string representation)
        """
        sql_type = sql_type.upper()
        return {
            'DECIMAL':'int', 'NUMERIC':'float', 'FLOAT':'float', 
            'DOUBLE':'float', 'INTEGER':'int', 'BIGINT':'int', 
            'CHAR':'string', 'VARCHAR':'string',
            'DATE':'int', 'BOOLEAN':'Boolean'}[sql_type]

    def _like_code(self, node):
        """ Generate code for evaluating LIKE expression.
        
        Args:
            node: describes LIKE expression
        
        Returns:
            code for evaluating LIKE expression
        """
        operands = node['operands']
        to_test = self._operation_code(operands[0])
        pattern = operands[1]['literal'].replace('%','.*')
        next_id = max(self.id2like.keys())+1 if self.id2like else 0
        self.id2like[next_id] = pattern
        pattern_name = f'pattern{next_id}'
        pred_code = f'lambda s:{pattern_name}.match(s) is not None'
        return f'map_column({to_test}, {pred_code})'
    
    def _literal_code(self, literal, embed=True):
        """ Produces a code snippet producing given literal.
        
        Args:
            literal: translate this literal into code
            embed: whether to embed literal in column
        
        Returns:
            code producing given literal
        """
        scale = self._get_scale(literal)
        value = literal['literal']
        sql_type = literal['type']['type']
        internal_type = self._internal_type(sql_type)
        if value is None:
            value = 'get_null()'
        else:
            if scale is None:
                if sql_type in ['CHAR', 'VARCHAR', 'TEXT']:
                    value = f"'{value}'"
            else:
                value = f'round({value}*1e{scale})'
        
        return f'fill_{internal_type}_column({value},1)' if embed else value
    
    def _LogicalAggregate(self, step):
        """ Produce code for aggregates (optionally with grouping). 
        
        Args:
            step: plan step representing aggregates
        
        Returns:
            code realizing aggregates
        """
        groups = step['group']
        if groups:
            return self._grouped_aggs_code(step)
        else:
            return self._ungrouped_aggs_code(step)
    
    def _LogicalFilter(self, step):
        """ Produce code for a filter.
        
        Args:
            step: plan step representing filter
        
        Returns:
            code realizing filter
        """
        result = self._result_name(step['id'])
        condition = step['condition']
        if 'op' in condition and condition['op']['name'] == 'AND':
            conjuncts = condition['operands']
        else:
            conjuncts = [condition]

        # Heuristic: sort predicates in ascending order of code length
        pred_codes = [self._operation_code(c) for c in conjuncts]
        pred_codes.sort(key=lambda c:len(c))

        parts = []
        for pred_code in pred_codes:
            parts += [f'if not is_empty(in_rel_1):']
            parts += [f'\tp_idx = {pred_code}']
            parts += [f'\tp_idx = scale_to_table(p_idx, "Boolean", in_rel_1)']
            parts += [f'\tin_rel_1 = filter_table(in_rel_1, p_idx)']
        
        parts += [f'{result} = in_rel_1']
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
        in_steps = [self.id_to_step[s_id] for s_id in inputs]
        in_arity = [self._get_arity(s) for s in in_steps]
        in_1_arity = in_arity[0]
        in_2_arity = in_arity[1]
        
        # in_1_id = inputs[0]
        # in_1_step = self.id_to_step[in_1_id]
        # in_1_arity = self._get_arity(in_1_step)
        
        step_id = step['id']
        result = self._result_name(step_id)
        join_pred = step['condition']
        conjuncts = dbz.util.get_conjuncts(join_pred)
        
        def is_eq_col_pred(pred):
            """ Returns true iff equality between two columns. """
            if pred['op']['kind'] == 'EQUALS' and \
                all('input' in op for op in pred['operands']):
                return True
            else:
                return False

        key_cols_1 = []
        key_cols_2 = []
        eq_preds = [c for c in conjuncts if is_eq_col_pred(c)]
        for eq_pred in eq_preds:
            col_idxs = [op['input'] for op in eq_pred['operands']]
            col_idx_1 = min(col_idxs)
            col_idx_2_raw = max(col_idxs)
            col_idx_2 = col_idx_2_raw - in_1_arity
            key_cols_1 += [col_idx_1]
            key_cols_2 += [col_idx_2]

        join_type = step['joinType']
        if join_type == 'full':
            raise ValueError('Full outer join is not supported!')
        type_to_def = {
            'left':'left_outer_join', 
            'right':'right_outer_join'}
        join_def = type_to_def.get(join_type, 'equality_join')
        
        if join_def == 'equality_join' and not key_cols_1 and not key_cols_2:
            op_code = 'cross_product(in_rel_1, in_rel_2)'
        else:
            if join_type == 'left':
                add_params = f'{in_2_arity}, '
            elif join_type == 'right':
                add_params = f'{in_1_arity}, '
            else:
                add_params = ''
            op_code = f'{join_def}(in_rel_1, in_rel_2, {add_params}' +\
                f'{str(key_cols_1)}, {str(key_cols_2)})'
        
        parts = [f'{result} = {op_code}']
        
        filter_preds = [c for c in conjuncts if not is_eq_col_pred(c)]
        if filter_preds:
            parts += [f'if not is_empty({result}):']
            parts += [f'\tin_rel_1 = {result}']
            filter_codes = []
            for filter_pred in filter_preds:
                filter_code = self._operation_code(filter_pred)
                filter_codes += [filter_code]
            parts += [f'\tp_idx = multiway_and([{", ".join(filter_codes)}])']
            parts += [f'\t{result} = filter_table({result}, p_idx)']
        
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
        parts += [f'result_cols = []']
        exprs = step['exprs']
        for expr in exprs:
            expr_code = self._operation_code(expr)
            expr_sql_type = expr['type']['type']
            expr_internal_type = self._internal_type(expr_sql_type)
            parts += [f'column = {expr_code}']
            parts += [f'column = scale_to_table(' +\
                      f'column, "{expr_internal_type}", in_rel_1)']
            parts += ['result_cols += [column]']
        parts += [f'{result} = create_table(result_cols)']
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
        parts = [f'{result} = in_rel_1']
        
        if 'collation' in step:
            collation = step['collation']
            sort_cols = []
            ascending = []
            for d in collation:
                field_idx = str(d['field'])
                flag = 'True' if d['direction'] == 'ASCENDING' else 'False'
                sort_cols += [field_idx]
                ascending += [flag]
            parts += [f'sort_cols = [{",".join(sort_cols)}]']
            parts += [f'ascending = [{",".join(ascending)}]']
            parts += [f'{result} = sort_wrapper({result}, sort_cols, ascending)']
        
        if 'fetch' in step:
            nr_rows = step['fetch']['literal']
            parts += [f'{result} = first_rows({result},{nr_rows})']
        
        return '\n'.join(parts)

    def _LogicalTableScan(self, step):
        """ Produces code for table scan.
        
        Args:
            step: plan step representing scan
        
        Returns:
            code realizing scan
        """
        table = step['table'][0]
        file_path = f'{self.paths.data_dir}/{table.lower()}.csv'
        scan_code = f'load_from_csv("{file_path}")'
        result = self._result_name(step['id'])
        parts = [f'{result} = {scan_code}']
        
        col_types = step['outputType']['fields']
        for col_idx, col_type in enumerate(col_types):
            parts += [f'col = get_column({result},{col_idx})']
            sql_type = col_type['type']
            cast_type = self._internal_type(sql_type)
            suffix = '_round' if cast_type == 'int' else ''
            fct_name = f'cast_to_{cast_type}{suffix}'
            parts += [f'col = {fct_name}(col)']
            parts += [f'{result} = set_column({result},{col_idx},col)']
        
        return '\n'.join(parts)
    
    def _LogicalValues(self, step):
        """ Uses rows specified as part of the query.
        
        Args:
            step: plan step specifying tuples
        
        Returns:
            code generating given tuples
        """
        result = self._result_name(step['id'])
        in_rows = step['tuples']
        out_rows = []
        for in_row in in_rows:
            out_row = []
            for in_field in in_row:
                out_field = self._literal_code(in_field, False)
                out_row += [out_field]
            out_rows += [out_row]
        
        to_path = f'{self.paths.tmp_dir}/{result}'
        df = pd.DataFrame(out_rows)
        df.to_csv(to_path, header=False, index=False)
        
        parts = []
        parts += [f'{result} = load_from_csv("{to_path}")']
        return '\n'.join(parts)
    
    def _nary_boolean_code(self, operation):
        """ Generate code realizing n-ary Boolean operator.
        
        Args:
            operation: translate this operation into code
        
        Returns:
            code realizing operation
        """
        op_kind = operation['op']['kind']
        op_name = {'AND':'multiway_and', 'OR':'multiway_or'}[op_kind]
        operands = operation['operands']
        op_sql_types = [op['type']['type'] for op in operands]
        op_internal_types = [self._internal_type(t) for t in op_sql_types]
        params = [self._operation_code(operand) for operand in operands]
        return f'{op_name}(scale_columns(' +\
            f'[{", ".join(params)}], ' +\
            f'{op_internal_types}))'
    
    def _operation_code(self, operation):
        """ Generate code realizing given operation. 
        
        Args:
            operation: translate this operation into code
        
        Returns:
            code for realizing operation
        """
        op_code = None
        if 'literal' in operation:
            op_code = self._literal_code(operation)
        elif 'input' in operation:
            op_code = self._column_code(operation)
        elif 'op' in operation:
            syntax = operation['op']['syntax']
            name = operation['op']['name']
            if name in ['AND', 'OR']:
                op_code = self._nary_boolean_code(operation)
            elif syntax == 'BINARY' or name in ['+', '-']:
                op_code = self._binary_code(operation)
            elif name == 'CASE':
                op_code = self._case_code(operation)
            elif name == 'CAST':
                # Unnecessary due to auto-casting
                op_code = self._cast_code(operation)
            elif name == 'EXTRACT':
                op_code = self._extract_code(operation)
            elif name in [
                'NOT', 'IS NULL', 'IS NOT NULL', 
                'IS TRUE', 'IS NOT TRUE', 
                'IS FALSE', 'IS NOT FALSE']:
                op_code = self._unary_code(operation)
            elif name == 'LIKE':
                op_code = self._like_code(operation)
            elif name == 'SUBSTRING':
                op_code = self._substring_code(operation)
        
        if op_code is None:
            raise ValueError(f'Unhandled operation: {operation}')
        else:
            sql_type = operation['type']['type']
            internal_type = self._internal_type(sql_type)
            suffix = '_round' if internal_type == 'int' else ''
            return f'cast_to_{internal_type}{suffix}({op_code})'
    
    def _post_code(self, final_step):
        """ Code for column-type specific post-processing. 
        
        Args:
            final_step: final step in query plan
        
        Returns:
            code for post-processing final result
        """
        parts = []
        col_types = final_step['outputType']['fields']
        for col_idx, col_type in enumerate(col_types):
            parts += [f'col = get_column(last_result,{col_idx})']
            base_type = col_type['type']
            if base_type in ['DECIMAL', 'NUMERIC']:
                if 'scale' in col_type:
                    scale = col_type['scale']
                    parts += [f'col = multiply_by_scalar(col, 1e-{scale})']
                    parts += [f'col = map_column(col, lambda i:round(i,{scale}))']
            elif base_type in ['CHAR']:
                length = col_type['precision']
                parts += [f'col = smart_padding(col, {length})']
            elif base_type in ['DATE']:
                parts += ['from datetime import date, timedelta']
                parts += ["ref_date = date(1970,1,1)"]
                parts += [
                    f'col = map_column(col, ' +\
                    f'lambda d:str(ref_date + timedelta(days=d)))']
                
            parts += [f'last_result = set_column(last_result, {col_idx}, col)'] 
        
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
        label = f'# Operation ID: {op_id}; Operator: {rel_op}'
        print(label)
         
        parts = []
        parts += [label]
        inputs = [self._result_name(in_) for in_ in step['inputs']]
        for idx, in_code in enumerate(inputs, 1):
            parts += [f'in_rel_{idx} = {in_code}']
        handler = f'_{rel_op}'
        parts += [getattr(self, handler)(step)]
        result = self._result_name(op_id)
        
        parts += [f'last_result = {result}']
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
        return f'substring({src},get_value({start},0),get_value({length},0))'
    
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
            op_code = f'is_null({op_code})'
        elif kind in ['IS_TRUE', 'IS_NOT_TRUE']:
            op_code = f'multiway_and([' +\
                f'logical_not(is_null({op_code})),' +\
                    f'{op_code}])'
        if kind in ['IS_FALSE', 'IS_NOT_FALSE']:
            op_code = f'multiway_and([' +\
                f'logical_not(is_null({op_code})),' +\
                    f'logical_not({op_code})])'
        if 'NOT' in kind:
            return f'logical_not({op_code})'
        else:
            return op_code
    
    def _ungrouped_aggs_code(self, step):
        """ Generate code for processing aggregates without grouping. 
        
        Args:
            step: processing step representing aggregation
        
        Returns:
            code for generating corresponding aggregates
        """
        step_id = step['id']
        aggs = step['aggs']
        result = self._result_name(step_id)
        parts = [f'result_cols = []']

        for agg in aggs:
            check_1 = 'not is_empty(in_rel_1)'
            check_2 = 'nr_rows(get_column(in_rel_1, 0))'
            parts += [f'if {check_1} and {check_2}:']
            
            kind = agg['agg']['kind']
            operands = agg['operands']
            if kind in ['SUM', 'AVG', 'MIN', 'MAX']:
                assert len(operands) == 1
                operand = operands[0]
                parts += [f'\tin_col = get_column(in_rel_1,{operand})']
                parts += [f'\tval = calculate_{kind.lower()}(in_col)']
                parts += ['\t# Ensure dependency to get_null() is registered']
                parts += ['\tget_null()']
            else:
                distinct = agg['distinct']
                params = f'in_rel_1, {str(operands)}, {distinct}'
                parts += [f'\tval = ungrouped_count({params})']
                
            parts += ['else:']
            def_val = '0' if agg['agg']['kind'] == 'COUNT' else 'get_null()'
            parts += [f'\tval = {def_val}']
            
            agg_sql_type = agg['type']['type']
            agg_internal_type = self._internal_type(agg_sql_type)
            parts += [f'agg_result = fill_{agg_internal_type}_column(val, 1)']
            parts += [f'result_cols += [agg_result]']
        
        parts += [f'{result} = create_table(result_cols)']
        return '\n'.join(parts)