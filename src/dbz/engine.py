'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
class Engine():
    """ Executes given query plans. """
    
    def __init__(self, library, data_dir, work_dir):
        """ Initializes with given paths.
        
        Args:
            library: library with operator code
            data_dir: directory containing data
            work_dir: path to working directory
        """
        self.library = library
        self.data_dir = data_dir
        self.work_dir = work_dir
        self.id_to_plan = {}
    
    def execute(self, plan):
        """ Execute given query plan.
        
        Args:
            plan: a query plan in JSON
        
        Returns:
            query result as data frame
        """
        return self.library + self._plan_code(plan)
    
    def _LogicalTableScan(self, step):
        """ Produces code for table scan.
        
        Args:
            step: plan step representing scan
        
        Returns:
            code realizing scan
        """
        db = step['table'][0]
        table = step['table'][1]
        file_path = f'{self.data_dir}/{db}/{table}'
        op_code = f'LogicalTableScan({file_path})'
        result = self._result_name(step)
        return f'{result} = {op_code}'
    
    def _plan_code(self, plan):
        """ Translates plan into code.
        
        Args:
            plan: query plan in JSON
        
        Returns:
            Python code (referencing library operators).
        """
        lines = []
        for step in plan['rels']:
            lines += [self._step_code(step)]
        return '\n'.join(lines)
    
    def _result_name(self, step):
        """ Returns name of intermediate result variable.
        
        Args:
            step: focus on variable storing result of this step
        
        Returns:
            name of variable storing intermediate result of step
        """
        return f"result_{step['id']}"
    
    def _step_code(self, step):
        """ Translates one plan step into code.
        
        Args:
            step: translate this plan step
        
        Returns:
            code for executing plan step
        """
        rel_op = step['relOp']
        handler = f'_{rel_op}'
        return getattr(self, handler)(step)