'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
import dbz.execute.engine
import dbz.generate.synthesize
import json
import logging
import openai.embeddings_utils
import os.path
import re


class Tasks():
    """ Stores and analyzes generation and verification tasks. """
    
    def __init__(self, config, substitutions):
        """ Loads and analyzes tasks.
        
        Args:
            config: JSON configuration file with task descriptions
            substitutions: custom prompt substitutions
            pre_code: code prefix provided by users
        """
        self.logger = logging.getLogger('all')
        self.logger.info('Initializing Tasks')
        self.config = config
        self.substitutions = substitutions
        test_access = self.config['test_access']
        data_dir = test_access['data_dir']
        self.paths = dbz.util.DbzPaths(
            data_dir, includes='src/dbz/include/trace')
        
        self.gen_tasks = self._ordered_tasks()
        self._add_context()
        self.id2task = {t['task_id']:t for t in self.gen_tasks}
        self._add_fct_names()
        self.check_tasks = self._check_tasks()
    
    def _add_context(self):
        """ Assign each generation task to most similar prior task. """
        for gen_task in self.gen_tasks:
            file_name = gen_task['template']
            substitutions = {**gen_task['substitutions'], **self.substitutions}
            prompt = dbz.generate.synthesize.Synthesizer.load_prompt(
                file_name, substitutions)
            embedding = openai.embeddings_utils.get_embedding(
                prompt, engine='code-search-babbage-code-001')
            gen_task['prompt_embedding'] = embedding
        
        for t_idx, task in enumerate(self.gen_tasks):
            embedding = task['prompt_embedding']
            prior_tasks = [self.gen_tasks[i] for i in range(t_idx)]
            task2similarity = {}
            for prior_task in prior_tasks:
                prior_id = prior_task['task_id']
                prior_embedding = prior_task['prompt_embedding']
                similarity = openai.embeddings_utils.cosine_similarity(
                    embedding, prior_embedding)
                task2similarity[prior_id] = similarity
            
            ranking = list(task2similarity.items())
            ranking.sort(key=lambda p:p[1], reverse=True)
            task['similar_tasks'] = ranking
            task_id = task['task_id']
            self.logger.info(f'Similar to {task_id}: {ranking[:2]}')
    
    def _add_fct_names(self):
        """ Add names of generated functions to task descriptions. """
        for gen_task in self.gen_tasks:
            file_name = gen_task['template']
            substitutions = gen_task['substitutions']
            prompt = dbz.generate.synthesize.Synthesizer.load_prompt(
                file_name, substitutions)
            
            name = self._fct_name(prompt)
            if name is not None:
                gen_task['function_name'] = name
            
            print(f'Function Name {gen_task["task_id"]}: {name}')
    
    def _add_requirements(self, check_task, trace_code):
        """ Determines requirements and adds them to task.
        
        Args:
            check_task: add requirements to this task
            trace_code: code for tracing requirements
        """
        trace_code = trace_code.replace('assert ', '')
        self.logger.debug(trace_code)
        requirements = set()
        exec(trace_code, {'requirements':requirements})
        check_task['requirements'] = requirements
    
    def _check_tasks(self):
        """ Generate list of checks with associated requirements. 
                
        Returns:
            a list of checks
        """
        tracer_lib = self._tracer_lib()
        engine = dbz.execute.engine.DbzEngine(self.paths, tracer_lib, None)
        
        check_tasks = []
        for sql in self.config['checks']['queries']:
            label = f'SQL: {sql}'
            print(f'Analyzing task {label} ...')
            check_task = {'query':sql, 'type':'sql', 'label':label}
            trace_code = engine.sql2code(sql, 'dummy_path')
            self._add_requirements(check_task, trace_code)
            check_tasks += [check_task]
            print(f'SQL Check: {check_task}')
        
        test_dirs = self.config['checks']['test_dirs']
        for test_dir in test_dirs:
            for file_name in os.listdir(test_dir):
                
                if file_name == '__init__.py':
                    continue
                
                test_path = os.path.join(test_dir, file_name)
                if os.path.isdir(test_path):
                    continue
                
                with open(test_path) as file:
                    raw_code = file.read()
                
                m = re.search('<SubstituteBy:((.)*)>', raw_code)
                if m is None:
                    codes_placeholders = [(raw_code, '')]
                else:
                    placeholder = m.group(0)
                    substitutes = m.group(1).split('|')
                    codes_placeholders = [
                        (raw_code.replace(placeholder, s), s)
                        for s in substitutes]
                        
                for code, placeholder in codes_placeholders:
                    label = f'{file_name} ({placeholder})'
                    print(f'Analyzing task {label} ...')
                    check_task = {
                        'file': file_name, 'code':code, 
                        'type':'code', 'label':label}
                    trace_code = engine.add_context(code)
                    self._add_requirements(
                        check_task, trace_code)
                    check_tasks += [check_task]
                    print(f'Added Code Check: {check_task}')
                    
        return check_tasks

    def _fct_name(self, prompt):
        """ Extract name of function to generate from prompt.
        
        Args:
            prompt: text of prompt initiating code generation
        
        Returns:
            name of Python function to generate
        """
        lines = prompt.split('\n')
        for line in lines:
            match = re.match('def\s(.*)\(.*', line)
            if match is not None:
                return match.group(1)
        
        return None
    
    def _prompt_length(self, task):
        """ Calculate length of code generation prompt.
        
        Args:
            task: calculate prompt length for this task
        
        Returns:
            length of prompt in characters
        """
        file_name = task['template']
        substitutions = {**task['substitutions'], **self.substitutions}
        prompt = dbz.generate.synthesize.Synthesizer.load_prompt(
            file_name, substitutions)
        return len(prompt)
    
    def _ordered_tasks(self):
        """ Optimize order of code generation tasks.
        
        Returns:
            ordered list of generation tasks
        """
        tasks = self.config['tasks']
        gen_tasks = [t for t in tasks if t['type'] == 'generate']
        id2task = {t['task_id']:t for t in gen_tasks}
        
        ordered_tasks = []
        groups = self.config['groups']
        for group in groups:
            self.logger.info(f'Group: {group["name"]}')
            group_task_ids = group['tasks']
            group_tasks = [id2task[t_id] for t_id in group_task_ids]
            group_tasks.sort(key=lambda t:self._prompt_length(t))
            ordered_tasks += group_tasks
        
        return ordered_tasks
        
    def _tracer_fct(self, fct_name, task_id):
        """ Write function for tracing required tasks. 
        
        Args:
            fct_name: name of tracer function to generate
            task_id: ID of task generating this function
        
        Returns:
            code recording task ID upon invocation
        """
        return f'def {fct_name}(*args):\n' +\
            f'\trequirements.add("{task_id}")\n' +\
            '\treturn []'
    
    def _tracer_lib(self):
        """ Write code for tracing required tasks.
        
        Returns:
            code piece recording required tasks
        """
        parts = []
        for gen_task in self.gen_tasks:
            task_id = gen_task['task_id']
            fct_name = gen_task['function_name']
            tracer_fct = self._tracer_fct(fct_name, task_id)
            parts += [tracer_fct]
        return '\n'.join(parts)


if __name__ == '__main__':
    
    with open('config/synthesis.json') as file:
        config = json.load(file)
    
    tasks = Tasks(config)
    print(tasks.gen_tasks)
    print(tasks.check_tasks)