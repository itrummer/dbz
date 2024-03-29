'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import dbz.check
import dbz.engine
import dbz.util
import json
import openai
import time


class Synthesizer():
    """ Synthesizes code for a DBMS engine. """
    
    def __init__(self, config_path, data_nl, operator_nl):
        """ Initialize for given natural language instructions.
        
        Args:
            config_path: path to configuration file
            data_nl: natural language description of data format
            operator_nl: natural language description of operators
        """
        with open(config_path) as file:
            self.config = json.load(file)
        self.data_nl = data_nl
        self.operator_nl = operator_nl
        self.solutions = {}
        self.solved_tasks = []
    
    def synthesize(self):
        """ Synthesize code for DBMS engine. 
        
        Returns:
            code defining table and operator implementations, statistics
        """
        print('Starting DBMS code synthesis ...')
        tasks = self.config['tasks']
        nr_tasks = len(tasks)
        temperature = 0
        task_idx = 0
        last_passed = -1
        
        stats = []
        while task_idx < nr_tasks:
            cur_task = tasks[task_idx]
            task_type = cur_task['type']
            print(f'Treating task {cur_task} ...')
            
            task_stats = {}
            task_stats['task_idx'] = task_idx
            task_stats['task'] = cur_task
            task_stats['temperature'] = temperature
            stats += [task_stats]
            
            start_s = time.time()
            if task_type == 'generate':
                solution = self._generate(cur_task, temperature)
                task_id = cur_task['task_id']
                self.solutions[task_id] = solution
                self.solved_tasks += [task_id]
                task_idx += 1
            elif task_type == 'check':
                success = self._check(cur_task)
                if success:
                    temperature = 0
                    last_passed = task_idx
                    task_idx += 1
                else:
                    temperature += 0.05
                    if temperature >= 1:
                        temperature = 0
                    task_idx = last_passed+1
                    self.solved_tasks = []
                    if last_passed >= 0:
                        for t in tasks[:last_passed]:
                            if t['type'] == 'generate':
                                task_id = t['task_id']
                                self.solved_tasks += [task_id]
            else:
                raise ValueError(f'Unknown task type: {task_type}')
            
            total_s = start_s - time.time()
            task_stats['total_s'] = total_s
        
        return self._library(), stats
    
    def _complete(self, prompt, temperature, stop):
        """ Use OpenAI's GPT-3 Codex model for completion.
        
        Args:
            prompt: complete this prompt
            temperature: degree of randomness
            stop: stop generation at this string
        
        Returns:
            completed code
        """
        print(f'--- PROMPT ---\n{prompt}')
        delay_s = 3
        for i in range(5):
            print(f'Querying Codex - retry nr. {i} ...')
            try:
                time.sleep(delay_s)
                response = openai.Completion.create(
                    prompt=prompt, stop=stop,
                    temperature=temperature,
                    engine='davinci-codex',
                    max_tokens=600)
                completion = response['choices'][0]['text']
                print(f'--- COMPLETION ---\n{completion}')
                return completion
            except openai.error.InvalidRequestError as e:
                print(f'Invalid OpenAI request: {e}')
                return None
            except Exception as e:
                print(f'Exception: {e}')
                delay_s *= 2
    
    def _check(self, task):
        """ Validate previously generated code pieces.
        
        Args:
            task: suggests SQL queries for verification
        
        Returns:
            true iff all queries are validated
        """
        ref_access = self.config['ref_access']
        pg_db = ref_access['pg_db']
        pg_user = ref_access['pg_user']
        pg_pwd = ref_access['pg_pwd']
        pg_host = ref_access['host']
        ref_engine = dbz.engine.PgEngine(pg_db, pg_user, pg_pwd, pg_host)
        
        test_access = self.config['test_access']
        data_dir = test_access['data_dir']
        python = test_access['python']
        paths = dbz.util.DbzPaths(data_dir)
        self.python_path = python
        queries = task['queries']
        
        test_engine = dbz.engine.DbzEngine(paths, self._library(), python)
        validator = dbz.check.Validator(paths, queries, ref_engine)
        return validator.validate(test_engine)
    
    def _generate(self, task, temperature):
        """ Synthesize code piece as described in task.
        
        Args:
            task: dictionary describing generation task
            temperature: degree of randomness in generation
        
        Returns:
            prompt with generated code piece
        """
        parts = []
        context = task['context']
        for c in context:
            parts += [self.solutions[c]]
        
        file = task['template']
        prompt_end = self._load_prompt(file)
        substitutions = task['substitutions']
        prompt_end = self._substitute(prompt_end, substitutions)
        parts += [prompt_end]
        
        prompt = '\n'.join(parts)
        stop = '\n\n'
        if 'stop' in task:
            stop = task['stop']
        completion = self._complete(prompt, temperature, stop)
                
        return prompt_end + completion + ('\n'*2)
    
    def _library(self):
        """ Assemble generated code for execution engine library. 
        
        Returns:
            code defining data structures and operators
        """
        parts = []
        for task_id in self.solved_tasks:
            solution = self.solutions[task_id]
            parts += [solution]
        return '\n'.join(parts)

    def _load_prompt(self, file_name):
        """ Load prompt (potentially with placeholders) from given file. """
        in_path = f'src/dbz/prompt/{file_name}'
        with open(in_path) as file:
            return file.read()
    
    def _operators(self):
        """ Generate code for relational operators. 
        
        Returns:
            code for relational operators
        """
        operators = []
        op_configs = self.config['operators']
        for op_file, op_instances in op_configs.items():
            for substitutions in op_instances:
                context = self.imports + '\n' + self.table + ('\n'*3)
                prompt = self._load_prompt(op_file)
                prompt = self._substitute(prompt, substitutions)
                completion = self._complete(context+prompt, 0, '\n'*2)
                operators += [prompt + '\n' + completion + ('\n'*2)]
        return operators
    
    def _substitute(self, raw_text, substitutions):
        """ Substitute placeholders by values.
        
        Args:
            raw_text: text with placeholders to substitute
            substitutions: list of dictionaries mapping placeholders to values
        
        Returns:
            text after replacements
        """
        text = raw_text
        substitutions['<DataInstructions>'] = self.data_nl
        substitutions['<OperatorInstructions>'] = self.operator_nl
        for placeholder, value in substitutions.items():
            text = text.replace(placeholder, value)
        return text