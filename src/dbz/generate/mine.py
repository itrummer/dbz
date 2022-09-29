'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
import numpy as np
import sklearn.linear_model

class CodeMiner():
    """ Mines operator implementations using GPT-3 Codex. """
    
    def __init__(self, operators, synthesizer):
        """ Initializes for given synthesizer.
        
        Args:
            operators: keeps track of generated operators
            synthesizer: used to generate operator code
        """
        self.operators = operators
        self.synthesizer = synthesizer
    
    def mine(self, task):
        """ Mine code for given generation task.
        
        Args:
            task: describes code generation task
        
        Returns:
            ID of generated code in operator library (None if unsuccessful)
        """
        task_id = task['task_id']
        for temperature_idx in range(11):
            temperature = temperature_idx * 0.1
            code = self.synthesizer.generate(task, temperature)
            code_id = self.operators.add_op(task_id, code, temperature)
            if code_id is not None:
                return code_id
        
        return None
    
    def _e_min_temp(self, t2samples, model):
        """ Calculate expected minimum temperature for new code.
        
        Args:
            t2samples: maps temperature to a number of samples
            model: predicts likelihood of new code from temperature
        
        Returns:
            expectation on minimum temperature
        """
        e_min = 0
        p_none = 1.0
        temps = list(t2samples.keys()).sort()
        for temperature in temps:
            nr_t_samples = t2samples[temperature]
            p_new = self._p_new(nr_t_samples, temperature, model)
            e_min += p_none * p_new * temperature
            p_none *= (1.0 - p_new)
        
        return e_min
    
    def _model(self, task):
        """ Creates a model linking temperature to probability of new code. 
        
        Args:
            task: describes the code generation task
        
        Returns:
            a linear model predicting new code probability from temperature
        """
        x = [0, 1.0/3, 2.0/3, 1]
        y = [0]
        for temperature in x[1:]:
            code = self.synthesizer.generate(task, temperature)
            y += [1] if self.operators.is_known(code) else [0]
        
        x = np.array(x).reshape((-1, 1))
        y = np.array(y)
        return sklearn.linear_model.LinearRegression(x, y)
    
    def _p_new(self, nr_t_samples, temperature, model):
        """ Calculates probability of retrieving new code.
        
        Args:
            nr_t_samples: number of code samples for temperature
            temperature: draw samples at this temperature
            model: predicts new code probability, given temperature
        
        Returns:
            probability that new code is generated at least once
        """
        p_per_sample = model.predict(temperature)
        p_per_sample_n = 1.0 - p_per_sample
        p_n = p_per_sample_n ** nr_t_samples
        return 1.0 - p_n