'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import dbz.analyze.component
import logging
import openai
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

    def call_history(self):
        """ Returns call history used for statistics.
        
        Returns:
            a dictionary mapping components to lists of calls
        """
        return {"synthesizer":self.history}
    
    def generate(self, task, temperature, composition, use_context=True):
        """ Synthesize code piece as described in task.
        
        Args:
            task: dictionary describing generation task
            temperature: degree of randomness in generation
            composition: selected operators in current composition
            use_context: whether to integrate context into prompt
        
        Returns:
            prompt with generated code piece
        """
        start_s = time.time()
        prompt, prompt_end = self.task_prompt(
            task, composition, use_context)
        stop = ['\n\n\n', '\ndef ', '\nif']
        if 'stop' in task:
            stop = task['stop']
        completion = self._complete(prompt, temperature, stop)
        
        total_s = time.time() - start_s
        task_id = task['task_id']
        self.history += [{
            "task_id":task_id,
            "temperature":temperature,
            "use_context":use_context,
            "prompt":prompt, 
            "prompt_end":prompt_end, 
            "completion":completion,
            "start_s":start_s,
            "total_s":total_s}]

        return prompt_end + completion + ('\n'*2)
    
    def task_prompt(self, task, composition, use_context=True):
        """ Generate prompt used for specific generation task and context.
        
        Args:
            task: dictionary describing operator generation task
            composition: maps task IDs to IDs of selected code pieces
            use_context: integrate context code snippets into prompt
        
        Returns:
            pair containing full prompt and last prompt piece
        """
        parts = []
        if self.prompt_prefix:
            parts += [self.prompt_prefix]
        
        if use_context:
            context = task['context']
            for c in context:
                ops = self.operators.get_ops(c)
                op_idx = composition[c]
                op = ops[op_idx]
                parts += [op]
        
        file = task['template']
        substitutions = {
            **task['substitutions'], 
            **self.def_substitutions}
        prompt_end = Synthesizer.load_prompt(
            file, substitutions) + self.prompt_suffix
        parts += [prompt_end]
        
        return '\n\n'.join(parts), prompt_end
    
    def _complete(self, prompt, temperature, stop):
        """ Use OpenAI's GPT-3 Codex model for completion.
        
        Args:
            prompt: complete this prompt
            temperature: degree of randomness
            stop: stop generation at this string
        
        Returns:
            completed code
        """
        logging.debug(f'--- PROMPT ---\n{prompt}')
        delay_s = 3
        for i in range(5):
            logging.info(f'Querying Codex - retry nr. {i} ...')
            try:
                time.sleep(delay_s)
                response = openai.Completion.create(
                    prompt=prompt, stop=stop,
                    temperature=temperature,
                    engine='code-davinci-002',
                    max_tokens=800)
                completion = response['choices'][0]['text']
                logging.debug(f'--- COMPLETION ---\n{completion}')
                return completion
            except openai.error.InvalidRequestError as e:
                logging.warning(f'Invalid OpenAI request: {e}')
                return None
            except Exception as e:
                logging.warning(f'Exception: {e}')
                delay_s *= 2