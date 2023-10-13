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
            self, operators, user_code_dir, synthesizer, 
            code_cache, nr_levels=4, must_contain=''):
        """ Initializes for given synthesizer.
        
        Args:
            operators: keeps track of generated operators
            user_code_dir: directory containing user code
            synthesizer: used to generate operator code
            code_cache: maps prompts to lists of generated code
            fct2tid: maps function names to task IDs
            nr_levels: how many temperature levels to consider
            must_contain: generated code must contain this string
        """
        super().__init__()
        self.logger = logging.getLogger('all')
        self.operators = operators
        self.user_code_dir = user_code_dir
        self.synthesizer = synthesizer
        self.code_cache = code_cache
        self.must_contain = must_contain
        
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
    
    def mine(self, composition, failure_info, task):
        """ Mine code as specified in given generation task.
        
        Args:
            composition: maps tasks to operator IDs
            failure_info: information about bugs in composition or None
            task: describes code generation task
        
        Returns:
            ID of newly generated code in operator library or None
        """
        task_id = task['task_id']
        code = self._get_user_code(task_id)
        
        if code is None:
            
            prompt, code = self._synthesize_code(
                composition, failure_info, task)
            if code is None:
                return None
            
            prior_cached = self.code_cache.get(prompt, [])
            self.code_cache[prompt] = prior_cached + [code]
        
        self.logger.info(f'Mined Code for Task {task_id}:\n{code}')
        return self.operators.add_op(task_id, code)
    
    def _get_cached(self, composition, failure_info, task, context_flags):
        """ Get unused code from cache for given task.
        
        Args:
            composition: maps task IDs to code IDs
            failure_info: information on current bugs
            task: describes a code generation task
            context_flags: whether to use code samples
        
        Returns:
            pair of unused code and associated prompt, or None pair
        """
        for use_context in context_flags:
            prompt_msgs, _ = self.synthesizer.chat_prompt(
                composition, failure_info, task, use_context)
            prompt = '\n'.join(m['content'] for m in prompt_msgs)
            self.logger.info(
                f'Check cache - prompt:' +\
                f'\n---\n{prompt}\n---\n')
            cached = self.code_cache.get(prompt, [])
            code = next((c for c in cached 
                if not self.operators.is_known(c)), None)
            if code is not None:
                self.logger.info(f'Found cached code:\n{code}')
                return code, prompt
        
        return None, None
    
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
    
    def _synthesize_code(self, composition, failure_info, task):
        """ Try to mine code via code synthesis. 

        Args:
            composition: maps tasks to operator IDs
            failure_info: info about bugs in composition
            task: description of generation task

        Returns:
            Prompt used, newly synthesized code (or None)
        """
        start_s = time.time()
        
        context_flags = [False, True] if task['similar_tasks'] else [False]
        code, prompt = self._get_cached(
            composition, failure_info, task, context_flags)
        
        synthesis_options = []
        for temperature in self.temperatures:
            for use_context in context_flags:
                synthesis_options += [(temperature, use_context)]
        
        if code is None:
            for temperature, use_context in synthesis_options:
                code = self.synthesizer.generate(
                    composition, failure_info, task,
                    temperature, use_context)
                
                if self.operators.is_known(code):
                    code = None
                elif self.must_contain not in code:
                    #code = None
                    pass
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