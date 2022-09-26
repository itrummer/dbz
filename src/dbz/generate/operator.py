'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
from collections import defaultdict

class Operators():
    """ Manages operator implementations. """
    
    def __init__(self):
        """ Initializes operator implementations. """
        self.ops_by_task = defaultdict(lambda:set())
        self.code_temp = defaultdict(lambda:1)
    
    def add_op(self, task_id, code, temperature):
        """ Adds operator implementation.
        
        Args:
            task_id: ID of operator generation task
            code: code of operator implementation
            temperature: generation temperature
        
        Returns:
            True if code was added (i.e., formerly unknown)
        """
        prior_temp = self.code_temp[code]
        self.code_temp[code] = min(prior_temp, temperature)
        ops = self.ops_by_task[task_id]
        if code in ops:
            return False
        else:
            ops.add(code)
            return True
    
    def get_ops(self, task_id):
        """ Retrieves operator implementations with temperatures.
        
        Args:
            task_id: the ID of the generation task
        
        Returns:
            list of (code,temperature) pairs, sorted by temperature (ascending)
        """
        ops = list(self.ops_by_task[task_id])
        ops_temp = [(op, self.code_temp[op]) for op in ops]
        ops_temp.sort(key=lambda o_t:o_t[1])
        return ops_temp


if __name__ == '__main__':
    
    ops = Operators()
    ops.add_op('test_task', 'print("hello!")', 1)
    ops.add_op('test_task', 'print("hello!")', 0.5)
    ops.add_op('test_task', 'print("hello world!")', 0.25)
    print(ops.get_ops('test_task'))