'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
import random


class Debugger():
    """ Traces unsolved checks based to faulty operator implementations. """
    
    def __init__(self, composer):
        """ Initializes with given composer. 
        
        Args:
            composer: composes the SQL execution engine
        """
        self.composer = composer
    
    def to_redo(self):
        """ Suggests generation task to redo. 
        
        Returns:
            ID of task to redo
        """
        checks = self.composer.failed_checks()
        task_ids = set()
        for check in checks:
            requirements = check['requirements']
            task_ids.update(requirements)
        
        if task_ids:
            return random.choice(list(task_ids))
        else:
            return 0