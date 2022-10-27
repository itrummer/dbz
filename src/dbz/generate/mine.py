'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
import logging


class CodeMiner():
    """ Mines code using GPT-3 Codex-based code synthesizer. """
    
    def __init__(
            self, operators, synthesizer, 
            code_cache, nr_levels=4, nr_samples=10):
        """ Initializes for given synthesizer.
        
        Args:
            operators: keeps track of generated operators
            synthesizer: used to generate operator code
            code_cache: maps prompts to lists of generated code
            nr_levels: how many temperature levels to consider
            nr_samples: try to limit to this number of samples
        """
        self.logger = logging.getLogger('all')
        self.operators = operators
        self.synthesizer = synthesizer
        self.code_cache = code_cache
        
        self.nr_levels = nr_levels
        self.nr_samples = nr_samples
        temperature_delta = 1.0 / nr_levels
        self.logger.debug(f'Temperature Delta: {temperature_delta}')
        self.temperatures = [
            temperature_delta * s for s in range(1, nr_levels+1)]
        self.logger.info(f'Temperatures Considered: {self.temperatures}')
    
    def mine(self, task, composition):
        """ Mine code as specified in given generation task.
        
        Args:
            task: describes code generation task
            composition: maps tasks to operator IDs
        
        Returns:
            ID of newly generated code in operator library
        """
        task_id = task['task_id']
        prompt, _ = self.synthesizer.task_prompt(task, composition)
        self.logger.info(f'Mining with Prompt:---\n{prompt}\n---\n')
        cached = self.code_cache.get(prompt, [])
        code = next((c for c in cached if not self.operators.is_known(c)), None)
        
        if code is None:
            if self.operators.get_ids(task_id):
                while code is None:
                    for temperature in self.temperatures:
                        code = self.synthesizer.generate(
                            task, temperature, composition)
                        code = self._normalize(code)
                        if self.operators.is_known(code):
                            code = None
                        else:
                            break
            else:
                code = self.synthesizer.generate(task, 0.0, composition)
                code = self._normalize(code)
        
        prior_cached = self.code_cache.get(prompt, [])
        self.code_cache[prompt] = prior_cached + [code]
        
        self.logger.info(f'Mined code for task {task_id}:\n{code}')
        return self.operators.add_op(task_id, code, -1)
    
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
    miner = CodeMiner(None, None, 4, 10)