'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
import filecmp
import os
import pandas as pd

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
        try:
            for idx, query in enumerate(self.queries, 1):
                print(f'Treating query {idx}/{self.nr_queries} ...')
                check_path = f'{self.paths.tmp_dir}/check_{idx}'
                engine.execute(query, check_path)
                ref_path = f'{self.paths.tmp_dir}/ref_{idx}'
                print('Start of test result:')
                print(os.system(f'head {check_path}'))
                print('Start of reference result:')
                print(os.system(f'head {ref_path}'))
                
                # Handle special case of empty files
                if filecmp.cmp(check_path, ref_path):
                    return True
                
                check_df = pd.read_csv(check_path, header=None)
                ref_df = pd.read_csv(ref_path, header=None)
                check_df.reindex()
                ref_df.reindex()
                
                try:
                    diffs = ref_df.compare(check_df, align_axis=0)
                    print(f'--- Differences ---\n{diffs}\n---')
                    nr_diffs = diffs.shape[0]
                except:
                    nr_diffs = 777

                if nr_diffs:
                    print(f'Result comparison failed for query {query}!')
                    return False
                else:
                    print(f'Validation successful!')
        
        except Exception as e:
            print(f'Validation failed with exception: {e}')
            return False
        return True

    def _generate_ref(self):
        """ Generates reference results for all queries. """
        print('Generating reference results ...')
        for idx, query in enumerate(self.queries, 1):
            print(f'Treating query {idx}/{self.nr_queries} ...')
            out = f'{self.paths.tmp_dir}/ref_{idx}'
            self.ref_engine.execute(query, out)