'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
import argparse
import dbz.execute.engine
import dbz.execute.query
import dbz.util
import filecmp
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
                print('Execution failed for reference engine - this should not happen!')
                return False
            
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
            if filecmp.cmp(check_path, ref_path):
                print(f'Validation successful!')
                return True
                            
            check_path = self._write_rounded(check_path, 2)
            ref_path = self._write_rounded(ref_path, 2)
                            
            check_df = pd.read_csv(check_path, header=None)
            ref_df = pd.read_csv(ref_path, header=None)
            
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
    
    def _write_rounded(self, in_path, precision):
        """ Write rounded version of .csv file to disk.
        
        Args:
            in_path: path to input .csv file
            precision: round to this precision (nr. digits)
        
        Returns:
            path to file with rounded values
        """
        df = pd.read_csv(in_path, header=None)
        out_path = in_path + '_rounded'
        df.to_csv(
            out_path, header=None, index=False, 
            float_format=f'%.{precision}f')
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