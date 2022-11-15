'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
from collections import defaultdict


class Operators():
    """ Manages operator implementations. """
    
    def __init__(self):
        """ Initializes operator implementations. """
        self.tid2ops = defaultdict(lambda:[])
        self.normalized_codes = set()
    
    def add_op(self, task_id, code):
        """ Adds operator implementation.
        
        Args:
            task_id: ID of operator generation task
            code: code of operator implementation
        
        Returns:
            Code index if code was added (otherwise None)
        """
        if self.is_known(code):
            return None
        else:
            normalized_code = self._normalize(code)
            self.normalized_codes.add(normalized_code)
            self.tid2ops[task_id] += [code]
            return len(self.tid2ops[task_id])-1
    
    def get_ids(self, task_id):
        """ Retrieves IDs of operator implementations.
        
        Args:
            task_id: the ID of the generation task
        
        Returns:
            list of operator code IDs
        """
        ops = self.tid2ops[task_id]
        nr_ops = len(ops)
        return list(range(nr_ops))
    
    def get_ops(self, task_id):
        """ Retrieves operator implementations with temperatures.
        
        Args:
            task_id: the ID of the generation task
        
        Returns:
            list of operator codes
        """
        return self.tid2ops[task_id]
    
    def is_known(self, code):
        """ Checks if operator code is known.
        
        Args:
            code: possibly new code for this task
        
        Returns:
            True iff the code is new
        """
        return self._normalize(code) in self.normalized_codes

    def _normalize(self, code):
        """ Normalize code by removing comments and empty lines.
        
        Args:
            code: code to normalize
        
        Returns:
            normalized code version
        """
        code_lines = code.split('\n')
        code_lines = filter(lambda l:l.lstrip(), code_lines)
        code_lines = filter(lambda l:not l.lstrip().startswith('#'), code_lines)
        return '\n'.join(code_lines)


if __name__ == '__main__':
    
    ops = Operators()
    ops.add_op('test_task', 'print("hello!")', 1)
    ops.add_op('test_task', 'print("hello!")', 0.5)
    ops.add_op('test_task', 'print("hello world!")', 0.25)
    print(ops.get_ops('test_task'))