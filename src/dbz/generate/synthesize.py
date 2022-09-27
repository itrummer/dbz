'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import openai
import random
import time


class Synthesizer():
    """ Synthesizes code for a DBMS engine. """
    
    def __init__(self, operators, table_nl, column_nl, tbl_post_nl):
        """ Initialize for given natural language instructions.
        
        Args:
            operators: manages operator implementations
            table_nl: natural language description of table representation
            column_nl: natural language description of column representation
            tbl_post_nl: natural language description of table post-processing
        """
        self.operators = operators
        self.def_substitutions = {
            '<Table>':table_nl, 
            '<Column>':column_nl, 
            '<TablePost':tbl_post_nl}

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
    
    def generate(self, task, temperature):
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
            ops_tmp = self.operators.get(c)
            op_tmp = random.choice(ops_tmp)
            parts += [op_tmp[0]]
        
        file = task['template']
        substitutions = {**task['substitutions'], **self.def_substitutions}
        prompt_end = Synthesizer.load_prompt(file, substitutions)
        parts += [prompt_end]
        
        prompt = '\n'.join(parts)
        stop = ['\n\n', 'def ']
        if 'stop' in task:
            stop = task['stop']
        completion = self._complete(prompt, temperature, stop)
                
        return prompt_end + completion + ('\n'*2)
    
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
                    #engine='davinci-codex',
                    engine='code-davinci-002',
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