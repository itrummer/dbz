'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
import argparse
import dbz.execute.engine
import dbz.execute.query
import dbz.util
import logging
import math
import os
import pandas as pd
import traceback


class Validator():
    """ Validates an engine implementation by comparing to reference. """
    
    def __init__(self, paths, sql_ref):
        """ Initializes validation for specific engine and queries.
        
        Args:
            paths: relevant paths for DB-zero
            sql_ref: generates reference results for SQL queries
        """
        self.paths = paths
        self.sql_ref = sql_ref
        self.logger = logging.getLogger('all')
    
    def validate(self, engine, check):
        """ Validate engine implementation by comparison to reference.
        
        Args:
            engine: validate this engine.
            check: validate using this test.
        
        Returns:
            True if validation succeeds.
        """
        print('Validation in progress ...')
        check_type = check['type']
        assert check_type in ['sql', 'code']
        if check_type == 'sql':
            return self._sql_check(engine, check)
        else:
            return self._code_check(engine, check)
    
    def _check_row_order(self, check):
        """ Determines whether check entails verifying the order of rows.
        
        Args:
            check: a check comparing results of two engines
        
        Returns:
            True iff different row orders entail a failed comparison
        """
        if check['type'] == 'sql':
            query = check['query']
            return 'order by' in query.lower()
        
        return False

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
            
            if not self._check_row_order(check):
                check_df.sort_values(
                    list(check_df.columns), inplace=True, ignore_index=True)
                ref_df.sort_values(
                    list(ref_df.columns), inplace=True, ignore_index=True)
            
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
    
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir', type=str, help='Path to data directory')
    parser.add_argument('lib_path', type=str, help='Path to library')
    parser.add_argument('python', type=str, help='Command for Python invocation')
    parser.add_argument('pg_db', type=str, help='Name of Postgres database')
    parser.add_argument('pg_user', type=str, help='Name of Postgres user')
    parser.add_argument('pg_pwd', type=str, help='Password for Postgres database')
    parser.add_argument('pg_host', type=str, help='Path to Postgres host')
    parser.add_argument('queries', type=str, help='Path to input queries')
    args = parser.parse_args()
    
    print(f'Comparing query results to Postgres on sample queries ...')
    paths = dbz.util.DbzPaths(args.data_dir)
    with open(args.lib_path) as file:
        library = file.read()
    dbz_engine = dbz.execute.engine.DbzEngine(
        paths, library, args.python)
    pg_engine = dbz.execute.engine.PgEngine(
        args.pg_db, args.pg_user, 
        args.pg_pwd, args.pg_host)
    
    queries = dbz.execute.query.load_queries(args.queries)
    queries = [dbz.execute.query.simplify(q) for q in queries]
    
    validator = Validator(paths, pg_engine)
    results = []
    for query in queries:
        check = {'query':query, 'type':'sql'}
        success = validator.validate(dbz_engine, check)
        results += [success]
    
    print(f'Checks Passed: {results}')
    print(f'Validation success: {success}')