'''
Created on Nov 21, 2022

@author: immanueltrummer
'''
import abc


@abc.ABC
class AnalyzedComponent():
    """ A system component whose call history is recorded and analyzed. """
    
    def __init__(self):
        """ Initializes call history. """
        self.history = []
    
    @abc.abstractmethod
    def call_history(self):
        """ Returns call history of this component. 
        
        Returns:
            a dictionary mapping sub-component keys to call logs
        """
        raise NotImplementedError()