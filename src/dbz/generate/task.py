'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
import dbz.execute.engine
import dbz.generate.synthesize
import json
import os.path
import re


class Tasks():
    """ Stores and analyzes generation and verification tasks. """
    
    def __init__(self, config):
        """ Loads and analyzes tasks.
        
        Args:
            config: JSON configuration file with task descriptions
        """
        self.config = config
        test_access = self.config['test_access']
        data_dir = test_access['data_dir']
        self.paths = dbz.util.DbzPaths(
            data_dir, includes='src/dbz/include/trace')
        
        tasks = config['tasks']
        self.gen_tasks = [t for t in tasks if t['type'] == 'generate']
        self.id2task = {t['task_id']:t for t in self.gen_tasks}
        self._add_fct_names()
        self.check_tasks = self._check_tasks()        
    
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
    
    def _check_tasks(self):
        """ Generate list of checks with associated requirements. 
                
        Returns:
            a list of checks
        """
        tracer_lib = self._tracer_lib()
        engine = dbz.execute.engine.DbzEngine(self.paths, tracer_lib, None)
        
        check_tasks = []
        for sql in self.config['checks']['queries']:
            check_task = {'query':sql, 'type':'sql'}
            trace_code = engine.sql2code(sql, 'dummy_path')
            self._add_requirements(check_task, trace_code)
            check_tasks += [check_task]
        
        test_dirs = self.config['checks']['test_dirs']
        for test_dir in test_dirs:
            for file_name in os.listdir(test_dir):
                
                if file_name == '__init__.py':
                    continue
                
                test_path = os.path.join(test_dir, file_name)
                with open(test_path) as file:
                    query_code = file.read()
                
                check_task = {'code':query_code, 'type':'code'}    
                trace_code = engine.add_context(query_code, 'dummy_path')
                self._add_requirements(check_task, trace_code)
                check_tasks += [check_task]
                    
        return check_tasks

    def _add_requirements(self, check_task, trace_code):
        """ Determines requirements and adds them to task.
        
        Args:
            check_task: add requirements to this task
            trace_code: code for tracing requirements
        """
        requirements = set()
        exec(trace_code, {'requirements':requirements})
        check_task['requirements'] = requirements

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