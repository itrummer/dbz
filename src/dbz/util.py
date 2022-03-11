'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
class DbzPaths():
    """ Stores relevant paths for DB-Zero. """
    
    def __init__(self, data_dir, python):
        """ Initializes all paths. 
        
        Args:
            data_dir: main data directory
            python: command for invoking Python
        """
        self.data_dir = data_dir
        self.config = f'config/synthesis.json'
        self.tmp_dir = f'{data_dir}/tmp'
        self.planner = 'jars/Planner.jar'
        self.code = f'{self.tmp_dir}/run_query.py'
        self.python = python


def load_queries(query_path):
    """ Load queries from a given file.
    
    Args:
        query_path: path to file containing queries
    
    Returns:
        cleaned-up queries
    """
    with open(query_path) as file:
        workload = file.read()
    queries = workload.split(';')
    def clean(query):
        query = query.replace('\n', ' ')
        query = query.replace('\t', '')
        if 'select' in query:
            trim_before = query.index('select')
            return query[trim_before:]
        else:
            return ''
    queries = [clean(q) for q in queries]
    return [q for q in queries if q]