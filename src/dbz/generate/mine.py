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
            ID of newly generated code in operator library or None
        """
        task_id = task['task_id']
        prompt, _ = self.synthesizer.task_prompt(task, composition)
        self.logger.info(f'Mining with Prompt:---\n{prompt}\n---\n')
        cached = self.code_cache.get(prompt, [])
        code = next((c for c in cached if not self.operators.is_known(c)), None)
        
        synthesis_options = []
        context_flags = [True, False] if task['context'] else [True]
        for temperature in self.temperatures:
            for use_context in context_flags:
                synthesis_options += [(temperature, use_context)]
        
        if code is None:
            if self.operators.get_ids(task_id):
                for temperature, use_context in synthesis_options:
                    code = self.synthesizer.generate(
                        task, temperature, 
                        composition, use_context)
                    
                    if self.operators.is_known(code):
                        code = None
                    else:
                        t_info = f'temperature: {temperature}'
                        c_info = f'use_context: {use_context}'
                        self.logger.info(
                            f'New code found using {t_info}; {c_info}')
                        break
            else:
                code = self.synthesizer.generate(task, 0.0, composition)
        
        if code is None:
            return None
        
        prior_cached = self.code_cache.get(prompt, [])
        self.code_cache[prompt] = prior_cached + [code]
        
        self.logger.info(f'Mined code for task {task_id}:\n{code}')
        return self.operators.add_op(task_id, code, -1)


if __name__ == '__main__':
    miner = CodeMiner(None, None, 4, 10)