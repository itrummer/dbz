'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
import argparse
import dbz.analyze.component
import dbz.execute.engine
import dbz.execute.query
import dbz.util
import logging
import math
import os
import pandas as pd
import sqlglot.expressions
import time
import traceback


class QueryInfo():
    """ Extracts information for result verification from SQL query. """
    
    def __init__(self, query):
        """ Extracts information from input query.
        
        Args:
            query: SQL query
        """
        parsed = sqlglot.parse_one(query)
        self.select_names = self._select_names(parsed)
        self.order_names = self._order_names(parsed)
    
    def _name(self, item):
        """ Extracts name for given item (e.g., a column). 
        
        Args:
            item: an item that appears in a list clause
        
        Returns:
            item name or empty string (if the name cannot be extracted)
        """
        if isinstance(item, sqlglot.expressions.Column):
            return item.sql()
        elif isinstance(item, sqlglot.expressions.Alias):
            return item.args['alias'].sql()
        else:
            return ''
    
    def _order_names(self, parsed):
        """ Extract names of items in order-by clause. 
        
        Args:
            parsed: input query in tree representation
        
        Returns:
            a list of item names
        """
        if not 'order' in parsed.args:
            return []
        
        order_clause = parsed.args['order']
        order_items = order_clause.args['expressions']
        return [self._name(i.args['this']) for i in order_items]
        
    
    def _select_names(self, parsed):
        """ Extract names of items in select clause.
        
        Args:
            parsed: tree representation of input query
        
        Returns:
            a list of item names
        """
        select_items = parsed.args.get('expressions', [])
        return [self._name(i) for i in select_items]


class Validator(dbz.analyze.component.AnalyzedComponent):
    """ Validates an engine implementation by comparing to reference. """
    
    def __init__(self, paths, sql_ref):
        """ Initializes validation for specific engine and queries.
        
        Args:
            paths: relevant paths for DB-zero
            sql_ref: generates reference results for SQL queries
        """
        super.__init__()
        self.paths = paths
        self.sql_ref = sql_ref
        self.logger = logging.getLogger('all')
    
    def call_history(self):
        """ Returns call history for all sub-components. 
        
        Returns:
            dictionary mapping sub-component IDs to call logs
        """
        return {
            "validator":self.history, 
            "ref_engine":self.sql_ref.stats
        }
    
    def validate(self, engine, check):
        """ Validate engine implementation by comparison to reference.
        
        Args:
            engine: validate this engine.
            check: validate using this test.
        
        Returns:
            True if validation succeeds.
        """
        print('Validation in progress ...')
        start_s = time.time()
        check_type = check['type']
        assert check_type in ['sql', 'code']
        if check_type == 'sql':
            success = self._sql_check(engine, check)
        else:
            success = self._code_check(engine, check)
        
        label = check['label']
        total_s = time.time() - start_s
        self.history += [{
            "check_type":check_type,
            "check_label":label,
            "total_s":total_s
            }]
        return success
    
    def _check_order_columns(self, check, nr_result_cols):
        """ Returns columns to sort by before result comparison.
        
        Args:
            check: columns refer to this check
            nr_result_cols: number of columns in result
        
        Returns:
            a list of column indexes
        """
        check_type = check['type']
        if not (check_type == 'sql'):
            return []
        else:
            query = check['query']
            query_info = QueryInfo(query)
            # Sort by all columns if no order specified
            order_names = query_info.order_names
            if not order_names:
                return list(range(nr_result_cols))
            else:
                # Do we know names of all select items?
                select_names = query_info.select_names
                if not (len(select_names) == nr_result_cols):
                    return []
                else:
                    # Return select items that do not appear in order-by clause
                    order_names = set(order_names)
                    return [
                        i for i in range(nr_result_cols) 
                        if select_names[i] not in order_names]

    def _code_check(self, engine, check):
        """ Validate a test case specified as code. 
        
        Args:
            engine: validate this engine
            check: a test case requiring code execution
        
        Returns:
            True iff the test was successful
        """
        code = check['code']
        code = engine.add_context(code)
        return engine.run(code)
    
    def _rounding(self, check_task):
        """ Create instructions for rounding before comparing results.
        
        Add rounding according to TPC-H specifications.
        
        Args:
            check_task: describes test to perform
        
        Returns:
            a dictionary containing rounding instructions
        """
        assert check_task['type'] == 'sql'
        query = check_task['query'].lower()
        first_select = query.split(' from ')[0]
        result_items = first_select.split(',')
        
        within_USD_100_cols = [
            i for i, s in enumerate(result_items) 
            if not 'sum(l_quantity)' in s and 
            not 'then 1 else 0 end' in s and 
            'sum(' in s]
        within_1_percent_cols = [
            i for i, s in enumerate(result_items)
            if 'avg(' in s or ' / ' in s]
        
        rounding = []
        rounding += [{
            "type":"absolute", "tolerance":100, 
            "columns":within_USD_100_cols}]
        rounding += [{
            "type":"relative", "tolerance":0.01,
            "columns":within_1_percent_cols}]
        
        return rounding
    
    def _round_dfs(self, check_df, ref_df, round_how):
        """ Rounds test and reference data as per instructions.
        
        Args:
            check_df: data to test for equivalence
            ref_df: ground truth data to compare against
            round_how: instructions on how to round
        
        Returns:
            pair of (rounded) check_df, ref_df
        """
        tolerance_type = round_how['type']
        cols_to_round = round_how['columns']
        for col_idx in cols_to_round:
            ref_col = ref_df.iloc[:,col_idx].astype('Float64')
            check_col = check_df.iloc[:,col_idx].astype('Float64')
            
            tolerance = round_how['tolerance']
            if tolerance_type == 'relative':
                ref_min = ref_col.min()
                tolerance = tolerance * ref_min
            
            self.logger.info(
                f'Rounding column {col_idx} with tolerance {tolerance} ...')
            if tolerance > 0:
                ref_col = ref_col.map(
                    lambda x:math.floor((x/tolerance)+0.5))
                check_col = check_col.map(
                    lambda x:math.floor((x/tolerance)+0.5))
                ref_df.iloc[:,col_idx] = ref_col
                check_df.iloc[:,col_idx] = check_col
        
        return ref_df, check_df
    
    def _sql_check(self, engine, check):
        """ Validates engine by comparing query result to reference.
        
        Args:
            engine: validate this engine
            check: describes query for result comparison
        
        Returns:
            True iff the test succeeds
        """
        try:
            query = check['query']
            ref_path = f'{self.paths.tmp_dir}/ref'
            check_path = f'{self.paths.tmp_dir}/check'
            
            ref_success = self.sql_ref.execute(query, ref_path)
            if not ref_success:
                raise Exception('Execution failed for reference engine!')
            
            success = engine.execute(query, check_path)
            print(f'Execution successful: {success}')
            if not success:
                print('Validation Failed!')
                return False
            
            ref_path = f'{self.paths.tmp_dir}/ref'
            print('Start of test result:')
            print(os.system(f'head {check_path}'))
            print('Start of reference result:')
            print(os.system(f'head {ref_path}'))
            
            # Handle special case of empty files
            with open(check_path) as file:
                test_data = file.read()
            with open(ref_path) as file:
                ref_data = file.read()
            if test_data == ref_data:
                print(f'Validation successful!')
                return True

            check_df = pd.read_csv(check_path, header=None)
            ref_df = pd.read_csv(ref_path, header=None)
            
            rounding = self._rounding(check)
            for round_how in rounding:
                check_df, ref_df = self._round_dfs(
                    check_df, ref_df, round_how)
                            
            check_path = self._write_rounded(check_df, check_path)
            ref_path = self._write_rounded(ref_df, ref_path)
            
            nr_check_cols = check_df.shape[1]
            nr_ref_cols = ref_df.shape[1]
            if not (nr_check_cols == nr_ref_cols):
                print(f'Different nr. columns: {nr_check_cols}, {nr_ref_cols}')
                return False
            
            sort_cols = self._check_order_columns(check, nr_ref_cols)
            if sort_cols:
                check_df.sort_values(
                    sort_cols, inplace=True, ignore_index=True)
                ref_df.sort_values(
                    sort_cols, inplace=True, ignore_index=True)

            try:
                diffs = ref_df.compare(check_df, align_axis=0)
                print(f'--- Differences ---\n{diffs}\n---')
                nr_diffs = diffs.shape[0]
            except Exception as e:
                print(f'Exception during comparison: {e}')
                nr_diffs = 777

            if nr_diffs:
                print(f'Result comparison failed!')
                return False
            else:
                print(f'Validation successful!')
                return True
        
        except Exception as e:
            print(f'Validation failed with exception: {e}')
            traceback.print_exc()
            return False
    
    def _write_rounded(self, df, in_path):
        """ Write rounded version of .csv file to disk.
        
        Args:
            df: a rounded data frame to write to disk
            in_path: path to input .csv file
        
        Returns:
            path to file with rounded values
        """
        out_path = in_path + '_rounded'
        df.to_csv(out_path, header=None, index=False)
        return out_path


if __name__ == '__main__':
    
    query = "SELECT c_custkey, c_name, SUM(l_extendedprice * (1 - l_discount)) AS revenue, c_acctbal, n_name, c_address, c_phone, c_comment FROM customer, orders, lineitem, nation WHERE c_custkey = o_custkey AND l_orderkey = o_orderkey AND o_orderdate >= date '1993-10-01' AND o_orderdate < date '1994-1-1' AND l_returnflag = 'R' AND c_nationkey = n_nationkey GROUP BY c_custkey, c_name, c_acctbal, c_phone, n_name, c_address, c_comment ORDER BY revenue DESC"
    qi = QueryInfo(query)
    print(qi.select_names)
    print(qi.order_names)
    validator = Validator(None, None)
    sort_cols = validator._check_order_columns({'type':'sql', 'query':query}, 8)
    print(sort_cols)
    
    # parser = argparse.ArgumentParser()
    # parser.add_argument('data_dir', type=str, help='Path to data directory')
    # parser.add_argument('lib_path', type=str, help='Path to library')
    # parser.add_argument('python', type=str, help='Command for Python invocation')
    # parser.add_argument('pg_db', type=str, help='Name of Postgres database')
    # parser.add_argument('pg_user', type=str, help='Name of Postgres user')
    # parser.add_argument('pg_pwd', type=str, help='Password for Postgres database')
    # parser.add_argument('pg_host', type=str, help='Path to Postgres host')
    # parser.add_argument('queries', type=str, help='Path to input queries')
    # args = parser.parse_args()
    #
    # print(f'Comparing query results to Postgres on sample queries ...')
    # paths = dbz.util.DbzPaths(args.data_dir)
    # with open(args.lib_path) as file:
        # library = file.read()
    # dbz_engine = dbz.execute.engine.DbzEngine(
        # paths, library, args.python)
    # pg_engine = dbz.execute.engine.PgEngine(
        # args.pg_db, args.pg_user, 
        # args.pg_pwd, args.pg_host)
        #
    # queries = dbz.execute.query.load_queries(args.queries)
    # queries = [dbz.execute.query.simplify(q) for q in queries]
    #
    # validator = Validator(paths, pg_engine)
    # results = []
    # for query in queries:
        # check = {'query':query, 'type':'sql'}
        # success = validator.validate(dbz_engine, check)
        # results += [success]
        #
    # print(f'Checks Passed: {results}')
    # print(f'Validation success: {success}')