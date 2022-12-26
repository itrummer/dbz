'''
Created on Dec 8, 2022

@author: immanueltrummer
'''
import re


class Tracer():
    """ Functions to trace dependencies between code pieces. """
    
    def __init__(self, definition_regex='def (.*)\(.*\):'):
        """ Initialize tracer function.
        
        Args:
            definition_regex: regular expression indicating function definition
        """
        self.definition_regex = definition_regex

    def definitions(self, code):
        """ Extracts names of functions defined in code piece.
        
        Args:
            code: analyze this code piece
        
        Returns:
            list of names of definitions (in definition order)
        """
        return re.findall(self.definition_regex, code)
    
    def relevant(self, target_code, parts):
        """ Identify directly relevant code parts for target code. 
        
        Args:
            target_code: identify relevant context for this code
            parts: list of code pieces that may contain relevant context
        
        Returns:
            list of code pieces that contain relevant definitions
        """
        relevant = []
        for part in parts:
            definitions = self.definitions(part)
            if any(
                re.search(f'\s+{d}\(', target_code) is not None 
                for d in definitions):
                relevant += [part]

        return relevant
    
    def relevant_transitive(self, target_code, parts):
        """ Identify directly and indirectly relevant code parts.
        
        Args:
            target_code: retrieve relevant context for this code
            parts: list of code pieces that may contain relevant context
        
        Returns:
            list of code pieces that are directly or indirectly relevant
        """
        changed = True
        while changed:
            changed = False
            relevant = self.relevant(target_code, parts)
            new_target = '\n'.join(relevant)
            if not (new_target == target_code):
                target_code = new_target
                changed = True
        
        return relevant


if __name__ == '__main__':
    tracer = Tracer()
    print(tracer.relevant(
        'def not_equal():\n\treturn False\n', 
        ['def equal():\n\treturn False\n',
         'def not_equal():\n\treturn True']))