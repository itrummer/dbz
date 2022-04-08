'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
import argparse
import dbz.engine
import dbz.query
import dbz.util
import filecmp
import os
import pandas as pd
import traceback


class Validator():
    """ Validates an engine implementation by comparing to reference. """
    
    def __init__(self, paths, queries, ref_engine):
        """ Initializes validation for specific engine and queries.
        
        Args:
            paths: relevant paths for DB-zero
            queries: compare results for those queries
            ref_engine: compare to results of reference
        """
        self.paths = paths
        self.queries = queries
        self.nr_queries = len(queries)
        self.ref_engine = ref_engine
        self._generate_ref()
    
    def validate(self, engine):
        """ Validate engine implementation by comparison to reference.
        
        Args:
            engine: validate this engine by comparison to reference results
        
        Returns:
            True if validation succeeds
        """
        print('Validation in progress ...')
        passed = True
        try:
            for idx, query in enumerate(self.queries, 1):
                print(f'Treating query {idx}/{self.nr_queries} ...')
                check_path = f'{self.paths.tmp_dir}/check_{idx}'
                success = engine.execute(query, check_path)
                print(f'Execution successful: {success}')
                if not success:
                    passed = False
                    continue
                
                ref_path = f'{self.paths.tmp_dir}/ref_{idx}'
                print('Start of test result:')
                print(os.system(f'head {check_path}'))
                print('Start of reference result:')
                print(os.system(f'head {ref_path}'))
                
                # Handle special case of empty files
                if filecmp.cmp(check_path, ref_path):
                    continue
                
                def write_rounded(in_path, precision):
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
                
                check_path = write_rounded(check_path, 2)
                ref_path = write_rounded(ref_path, 2)
                                
                check_df = pd.read_csv(check_path, header=None)
                ref_df = pd.read_csv(ref_path, header=None)
                
                if not 'order by' in query.lower():
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
                    print(f'Result comparison failed for query {query}!')
                    passed = False
                else:
                    print(f'Validation successful!')
        
        except Exception as e:
            print(f'Validation failed with exception: {e}')
            traceback.print_exc()
            return False
        return passed

    def _generate_ref(self):
        """ Generates reference results for all queries. """
        print('Generating reference results ...')
        for idx, query in enumerate(self.queries, 1):
            print(f'Treating query {idx}/{self.nr_queries} ...')
            out = f'{self.paths.tmp_dir}/ref_{idx}'
            self.ref_engine.execute(query, out)


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
    dbz_engine = dbz.engine.DbzEngine(
        paths, library, args.python)
    pg_engine = dbz.engine.PgEngine(
        args.pg_db, args.pg_user, 
        args.pg_pwd, args.pg_host)
    
    queries = dbz.query.load_queries(args.queries)
    queries = [dbz.query.simplify(q) for q in queries]
    
    validator = Validator(paths, queries, pg_engine)
    success = validator.validate(dbz_engine)
    print(f'Validation success: {success}')