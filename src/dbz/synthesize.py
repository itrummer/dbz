'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import openai
import time


class Synthesizer():
    """ Synthesizes code for a DBMS engine. """
    
    def __init__(self, config, data_nl, operator_nl):
        """ Initialize for given natural language instructions.
        
        Args:
            config: dictionary configuring the synthesis process
            data_nl: natural language description of data format
            operator_nl: natural language description of operators
        """
        self.config = config
        self.data_nl = data_nl
        self.operator_nl = operator_nl
        self.imports = None
        self.table = None
        self.operators = None
    
    def synthesize(self):
        """ Synthesize code for DBMS engine. 
        
        Returns:
            code defining table and operator implementations
        """
        print('Starting DBMS code synthesis ...')
        self.imports = self._imports()
        self.table = self._table()
        self.operators = self._operators()
        return '\n'.join([self.imports, self.table] + self.operators)
    
    def _complete(self, prompt, temperature, stop):
        """ Use OpenAI's GPT-3 Codex model for completion.
        
        Args:
            prompt: complete this prompt
            temperature: degree of randomness
            stop: stop generation at this string
        
        Returns:
            completed code
        """
        delay_s = 1
        for i in range(5):
            print(f'Querying Codex - retry nr. {i} ...')
            try:
                response = openai.Completion.create(
                    prompt=prompt, stop=stop,
                    temperature=temperature)
                return response['choices'][0]['text']
            except openai.error.InvalidRequestError as e:
                print(f'Invalid OpenAI request: {e}')
                return None
            except Exception as e:
                print(f'Exception: {e}')
                time.sleep(delay_s)
                delay_s *= 2
    
    def _imports(self):
        """ Generates code importing relevant libraries. 
        
        Returns:
            code importing relevant libraries
        """
        prompt = self._load_prompt('imports.py')
        prompt = self._substitute(prompt, [])
        completion = self._complete(prompt, 0, 'print(')
        return prompt + '\n' + completion
    
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
                prompt = self._load_prompt(op_file)
                prompt = self._substitute(prompt, substitutions)
                completion = self._complete(prompt, 0, '"""')
                operators += [prompt + '\n' + completion]
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
    
    def _table(self):
        """ Generates code for table class. 
        
        Returns:
            code defining class representing tables
        """
        prompt = self._load_prompt('table.py')
        prompt = self._substitute(prompt, [])
        completion = self._complete(prompt, 0, '"""')
        return prompt + '\n' + completion