'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
from collections import defaultdict

class Operators():
    """ Manages operator implementations. """
    
    def __init__(self):
        """ Initializes operator implementations. """
        self.ops_by_task = defaultdict(lambda:[])
        self.code_temp = {}
    
    def add_op(self, task_id, code, temperature):
        """ Adds operator implementation.
        
        Args:
            task_id: ID of operator generation task
            code: code of operator implementation
            temperature: generation temperature
        
        Returns:
            Code index if code was added (otherwise None)
        """
        if self.is_known(code):
            prior_temp = self.code_temp[code]
            next_temp = min(prior_temp, temperature)
            self.code_temp[code] = next_temp
            return None
        else:
            self.code_temp[code] = temperature
            self.ops_by_task[task_id] += [code]
            return len(self.ops_by_task[task_id])-1
    
    def get_ids(self, task_id):
        """ Retrieves IDs of operator implementations.
        
        Args:
            task_id: the ID of the generation task
        
        Returns:
            list of operator code IDs
        """
        ops = self.ops_by_task[task_id]
        nr_ops = len(ops)
        return list(range(nr_ops))
    
    def get_ops(self, task_id):
        """ Retrieves operator implementations with temperatures.
        
        Args:
            task_id: the ID of the generation task
        
        Returns:
            list of (code,temperature) pairs
        """
        ops = self.ops_by_task[task_id]
        return [(op, self.code_temp[op]) for op in ops]
    
    def is_known(self, code):
        """ Checks if operator code is known.
        
        Args:
            code: possibly new code for this task
        
        Returns:
            True iff the code is new
        """
        return code in self.code_temp

if __name__ == '__main__':
    
    ops = Operators()
    ops.add_op('test_task', 'print("hello!")', 1)
    ops.add_op('test_task', 'print("hello!")', 0.5)
    ops.add_op('test_task', 'print("hello world!")', 0.25)
    print(ops.get_ops('test_task'))