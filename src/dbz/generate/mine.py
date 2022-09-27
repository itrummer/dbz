'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
class CodeMiner():
    """ Mines operator implementations using GPT-3 Codex. """
    
    def __init__(self, operators, synthesizer):
        """ Initializes for given synthesizer.
        
        Args:
            operators: keeps track of generated operators
            synthesizer: used to generate operator code
        """
        self.operators = operators
        self.synthesizer = synthesizer
    
    def mine(self, task):
        """ Mine code for given generation task.
        
        Args:
            task: describes code generation task
        
        Returns:
            ID of generated code in operator library (None if unsuccessful)
        """
        task_id = task['task_id']
        for temperature_idx in range(11):
            temperature = temperature_idx * 0.1
            code = self.synthesizer.generate(task, temperature)
            code_id = self.operators.add_op(task_id, code, temperature)
            if code_id is not None:
                return code_id
        
        return None