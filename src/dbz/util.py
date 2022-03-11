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