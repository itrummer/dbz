'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
import dbz.analyze.component
import logging
import os.path
import time


class CodeMiner(dbz.analyze.component.AnalyzedComponent):
    """ Mines code using GPT-3 Codex-based code synthesizer. """
    
    def __init__(
            self, operators, user_code_dir, 
            synthesizer, code_cache, nr_levels=4):
        """ Initializes for given synthesizer.
        
        Args:
            operators: keeps track of generated operators
            user_code_dir: directory containing user code
            synthesizer: used to generate operator code
            code_cache: maps prompts to lists of generated code
            nr_levels: how many temperature levels to consider
        """
        super().__init__()
        self.logger = logging.getLogger('all')
        self.operators = operators
        self.user_code_dir = user_code_dir
        self.synthesizer = synthesizer
        self.code_cache = code_cache
        
        self.nr_levels = nr_levels
        temperature_delta = 1.0 / nr_levels
        self.logger.debug(f'Temperature Delta: {temperature_delta}')
        self.temperatures = [
            temperature_delta * s for s in range(0, nr_levels+1)]
        self.logger.info(f'Temperatures Considered: {self.temperatures}')
    
    def call_history(self):
        """ Returns history of mining calls.
        
        Returns:
            dictionary mapping component IDs to lists of calls
        """
        return {"miner":self.history}
        
    
    def mine(self, task, composition):
        """ Mine code as specified in given generation task.
        
        Args:
            task: describes code generation task
            composition: maps tasks to operator IDs
        
        Returns:
            ID of newly generated code in operator library or None
        """
        task_id = task['task_id']
        code = self._get_user_code(task_id)
        
        if code is None:
            
            prompt, code = self._synthesize_code(task, composition)
            if code is None:
                return None
            
            prior_cached = self.code_cache.get(prompt, [])
            self.code_cache[prompt] = prior_cached + [code]
        
        self.logger.info(f'Mined Code for Task {task_id}:\n{code}')
        return self.operators.add_op(task_id, code)
    
    def _get_user_code(self, task_id):
        """ Try to retrieve user-specified code for task.
        
        Args:
            task_id: ID of generation task
        
        Returns:
            code specified by user or None
        """
        file_name = f'{task_id}.py'
        full_path = os.path.join(self.user_code_dir, file_name)
        try:
            with open(full_path) as file:
                code = file.read()
                return code
        except:
            return None
    
    def _synthesize_code(self, task, composition):
        """ Try to mine code via code synthesis. 
        
        Args:
            task: description of generation task
            composition: maps tasks to operator IDs
        
        Returns:
            Prompt used, newly synthesized code (or None)
        """
        start_s = time.time()
        prompt, _ = self.synthesizer.task_prompt(task, composition)
        self.logger.info(f'Mining with Prompt:\n---\n{prompt}\n---\n')
        cached = self.code_cache.get(prompt, [])
        code = next((c for c in cached if not self.operators.is_known(c)), None)
        
        synthesis_options = []
        context_flags = [True, False] if task['similar_tasks'] else [True]
        for temperature in self.temperatures:
            for use_context in context_flags:
                synthesis_options += [(temperature, use_context)]
        
        if code is None:
            for temperature, use_context in synthesis_options:
                code = self.synthesizer.generate(
                    task, temperature, 
                    composition, use_context)
                
                if self.operators.is_known(code):
                    code = None
                else:
                    total_s = time.time() - start_s
                    t_info = f'temperature: {temperature}'
                    c_info = f'use_context: {use_context}'
                    self.logger.info(f'New code found via {t_info}; {c_info}')
                    task_id = task['task_id']
                    self.history += [{
                        "task_id":task_id,
                        "temperature":temperature,
                        "use_context":use_context,
                        "start_s":start_s,
                        "total_s":total_s,
                        "code":code
                        }]
                    break
        
        return prompt, code


if __name__ == '__main__':
    miner = CodeMiner(None, None, 4, 10)