'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
import dbz.execute.engine
import dbz.generate.synthesize
import json
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
        self._add_fct_names()
        self.check_tasks = self._check_tasks(tasks)        
    
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
    
    def _check_tasks(self, all_tasks):
        """ Generate list of checks with associated requirements. 
        
        Args:
            all_tasks: check and generation tasks
        
        Returns:
            a list of checks
        """
        tracer_lib = self._tracer_lib()
        engine = dbz.execute.engine.DbzEngine(self.paths, tracer_lib, None)
        
        check_tasks = []
        for t in all_tasks:
            if t['type'] == 'check':
                for sql in t['queries']:
                    check_task = {'query':sql}
                    requirements = set(t['context'])
                    code = engine.code(sql, 'dummy_path')
                    exec(code, {'requirements':requirements})
                    check_task['requirements'] = requirements
                    check_tasks += [check_task]
                    
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