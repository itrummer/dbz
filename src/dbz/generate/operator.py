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
        self.normalized2id = {}
        self.tid2did = {}
    
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
            new_op_id = len(self.tid2ops[task_id])
            self.normalized2id[normalized_code] = new_op_id
            self.tid2ops[task_id] += [code]
            return new_op_id
    
    def get_code_id(self, code):
        """ Retrieves ID of known code. 
        
        Args:
            code: look up ID for this code (non-normalized)
        
        Returns:
            ID of known code
        """
        normalized_code = self._normalize(code)
        return self.normalized2id[normalized_code]
    
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
    
    def is_default(self, task_id, code_id):
        """ Checks if code is default implementation.
        
        Args:
            task_id: check refers to this task
            code_id: check this implementation
        
        Returns:
            True iff given code is default for given task
        """
        return self.tid2did.get(task_id) == code_id
    
    def is_known(self, code):
        """ Checks if operator code is known.
        
        Args:
            code: possibly new code for this task
        
        Returns:
            True iff the code is new
        """
        return self._normalize(code) in self.normalized2id

    def mark_default(self, task_id, code_id):
        """ Mark operator code as default implementation.
        
        Args:
            task_id: mark default implementation for this task
            code_id: code ID of default operator implementation
        """
        self.tid2did[task_id] = code_id

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