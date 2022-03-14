'''
Created on Mar 9, 2022

@author: immanueltrummer
'''
class DbzPaths():
    """ Stores relevant paths in DB-Zero data directory. """
    
    def __init__(self, data_dir):
        """ Initializes all paths. 
        
        Args:
            data_dir: main data directory
        """
        self.data_dir = data_dir
        self.tmp_dir = f'{data_dir}/tmp'
        self.planner = 'jars/Planner.jar'
        self.code = f'{self.tmp_dir}/run_query.py'