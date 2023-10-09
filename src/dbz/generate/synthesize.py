'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import dbz.analyze.component
import dbz.generate.tracer
import logging
import openai
import re
import time


class Synthesizer(dbz.analyze.component.AnalyzedComponent):
    """ Synthesizes code for a DBMS engine. """
    
    def __init__(self, operators, substitutions, prompt_prefix, prompt_suffix):
        """ Initialize for given natural language instructions.
        
        Args:
            operators: manages operator implementations
            substitutions: maps placeholders to natural language instructions
            prompt_prefix: a code snippet used as prompt prefix
            prompt_suffix: a code snippet used as prompt suffix
        """
        super().__init__()
        self.operators = operators
        self.def_substitutions = substitutions
        self.prompt_prefix = prompt_prefix
        self.prompt_suffix = prompt_suffix
        self.tracer = dbz.generate.tracer.Tracer()

    @staticmethod    
    def load_prompt(file_name, substitutions):
        """ Load prompt from file and substitute placeholders. 
        
        Args:
            file_name: name of file containing prompt template
            substitutions: dictionary mapping placeholders to values
        
        Returns:
            text prompt after substitutions
        """
        in_path = f'src/dbz/prompt/{file_name}'
        with open(in_path) as file:
            text = file.read()

        for placeholder, value in substitutions.items():
            text = text.replace(placeholder, value)
        
        return text

    @staticmethod
    def function_name(task):
        """ Determine name of generated function.
        
        Args:
            task: extract function name from this task's prompt
        
        Returns:
            name of Python function associated with task
        """
        substitutions = task['substitutions']
        file_name = task['template']
        prompt = Synthesizer.load_prompt(file_name, substitutions)
        
        lines = prompt.split('\n')
        for line in lines:
            match = re.match('def\s(.*)\(.*', line)
            if match is not None:
                return match.group(1)
        
        return None

    def call_history(self):
        """ Returns call history used for statistics.
        
        Returns:
            a dictionary mapping components to lists of calls
        """
        return {"synthesizer":self.history}
    
    def generate(
            self, composition, failure_info, task,
            temperature, use_context=True):
        """ Synthesize code piece as described in task.
        
        Args:
            composition: selected operators in current composition
            failure_info: information on bugs in composition or None
            task: dictionary describing generation task
            temperature: degree of randomness in generation
            use_context: whether to integrate context into prompt
        
        Returns:
            prompt with generated code piece
        """
        start_s = time.time()
        prompt_msgs, prompt_end = self.chat_prompt(
            composition, failure_info, task, use_context)
        stop = ['\nif']
        if 'stop' in task:
            stop = task['stop']
        completion = self._complete(prompt_msgs, temperature, stop)
        all_functions = prompt_end + '\n' + completion
        pruned_code = self._prune(prompt_end, all_functions)
        
        total_s = time.time() - start_s
        task_id = task['task_id']
        self.history += [{
            "task_id":task_id,
            "temperature":temperature,
            "use_context":use_context,
            "prompt_msgs":prompt_msgs, 
            "prompt_end":prompt_end, 
            "completion":completion,
            "pruned_code":pruned_code,
            "start_s":start_s,
            "total_s":total_s}]

        return pruned_code
    
    def nr_characters(self):
        """ The number of characters processed by the generative model.
        
        Returns:
            the number of characters read or written by the model
        """
        total_chars = 0
        for call in self.history:
            total_chars += len(call['prompt']) + len(call['completion'])
        return total_chars
    
    def chat_prompt(self, composition, failure_info, task, use_context=True):
        """ Generate prompt for chat models describing generation task.
        
        Args:
            composition: maps task IDs to IDs of selected code pieces
            failure_info: information about bugs in composition or None
            task: dictionary describing operator generation task
            use_context: integrate context code snippets into prompt
        
        Returns:
            pair containing list of prompt messages and last prompt piece
        """
        parts = []
        if self.prompt_prefix:
            parts += [self.prompt_prefix]
        
        if use_context:
            sample_code = self._context(task, composition)
            if sample_code is not None:
                parts += [sample_code]
        
        file = task['template']
        substitutions = {
            **task['substitutions'], 
            **self.def_substitutions}
        prompt_end = Synthesizer.load_prompt(
            file, substitutions) + self.prompt_suffix
        parts += [prompt_end]
        
        initial_prompt = '\n\n\n'.join(parts)
        initial_msg = {'role':'user', 'content':initial_prompt}
        prompt_msgs = [initial_msg]
        
        if failure_info is not None:
            task_id = task['task_id']
            ops = self.operators.get_ops(task_id)
            code_id = composition[task_id]
            prior_op = ops[code_id]
            code_msg = {'role':'assistant', 'content':prior_op}
            prompt_msgs += [code_msg]
            
            error_lines = [
                'This code does not work. The following messages are possibly related:']
            error_lines += failure_info.error_lines
            error_content = '\n'.join(error_lines)
            error_msg = {'role':'user', 'content':error_content}
            prompt_msgs += [error_msg]
        
        return prompt_msgs, prompt_end
    
    def _complete(self, prompt_msgs, temperature, stop):
        """ Use OpenAI's GPT models for completion.
        
        Args:
            prompt_msgs: list of prompt messages
            temperature: degree of randomness
            stop: stop generation at this string
        
        Returns:
            completed code
        """
        logging.debug(f'--- PROMPT ---\n{prompt_msgs}')
        delay_s = 3
        for i in range(5):
            logging.info(f'Querying GPT - retry nr. {i} ...')
            try:
                time.sleep(delay_s)
                response = openai.ChatCompletion.create(
                    messages=prompt_msgs, stop=stop, temperature=temperature,
                    model='gpt-3.5-turbo', max_tokens=800)
                completion = response['choices'][0]['message']['content']
                logging.debug(f'--- COMPLETION ---\n{completion}')
                return completion
            except openai.error.InvalidRequestError as e:
                logging.warning(f'Invalid OpenAI request: {e}')
                return None
            except Exception as e:
                logging.warning(f'Exception: {e}')
                delay_s *= 2
        
    def _context(self, task, composition):
        """ Find code sample to facilitate code generation. 
        
        Args:
            task: find context to facilitate this task
            composition: maps tasks to code IDs
        
        Returns:
            most similar task code that is not default implementation (or None)
        """
        related_tids = [t[0] for t in task['similar_tasks']]
        for rid in related_tids:
            codes = self.operators.get_ops(rid)
            code_id = composition[rid]
            if not self.operators.is_default(rid, code_id):
                return codes[code_id]
        
        return None
    
    def _prune(self, target_code, generated_code):
        """ Prune generated code to keep only relevant content.
        
        Args:
            target_code: only keep code pieces referenced here
            generated_code: prune this code using target code
        
        Returns:
            pruned version of generated code
        """
        parts = generated_code.split('\n\n\n')
        parts = self.tracer.relevant_transitive(target_code, parts)
        code = '\n\n\n'.join(parts)
        return code.rstrip('\n')