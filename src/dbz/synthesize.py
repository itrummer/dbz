'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import openai


class Synthesizer():
    """ Synthesizes code for a DBMS engine. """
    
    def __init__(self, data_nl, operator_nl):
        """ Initialize for given natural language instructions.
        
        Args:
            data_nl: natural language description of data format
            operator_nl: natural language description of operators
        """
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
    
    def _complete(self, prompt, temperature):
        """ Use OpenAI's GPT-3 Codex model for completion.
        
        Args:
            prompt: complete this prompt
            temperature: degree of randomness
        
        Returns:
            completed code
        """
        pass
    
    def _load_prompt(self, file_name):
        """ Load prompt (potentially with placeholders) from given file. """
        in_path = f'src/dbz/prompt/{file_name}'
        with open(in_path) as file:
            return file.read()
    
    def _table(self):
        """ Generates code for table class. """
        prompt = self._load_prompt('table.py')