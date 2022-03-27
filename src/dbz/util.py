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
        self.schema = f'{data_dir}/schema.sql'
        self.tmp_dir = f'{data_dir}/tmp'
        self.planner = 'jars/Planner.jar'
        self.code = f'{self.tmp_dir}/run_query.py'
        

def get_conjuncts(expression):
    """ Decomposes AND expressions in query plans into components.
    
    Args:
        expression: an expression, potentially AND expression
    
    Returns:
        list of conjuncts or original expression (if not AND expression)
    """
    if 'op' in expression and expression['op']['kind'] == 'AND':
        operands = expression['operands']
        return [c for o in operands for c in get_conjuncts(o)]
    elif 'literal' in expression and expression['literal']:
        return []
    else:
        return [expression]