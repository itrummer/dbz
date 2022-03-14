'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
import filecmp
import os

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
                out = f'{self.paths.tmp_dir}/check_{idx}'
                engine.execute(query, out)
                ref = f'{self.paths.tmp_dir}/ref_{idx}'
                if filecmp.cmp(out, ref):
                    print(f'Validation successful.')
                else:
                    print(f'Result comparison failed for query {query}!')
                    print('Start of reference result:')
                    print(os.system(f'head {ref}'))
                    print('Start of test result:')
                    print(os.system(f'head {out}'))
                    return False
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