'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
from collections import Counter, defaultdict
from dataclasses import dataclass
import logging
import numpy as np
import sklearn.linear_model


@dataclass
class TemperatureStats():
    """ Statistics about specific temperature level. """
    nr_tries: int = 0
    nr_new: int = 0
    
    def new_ratio(self):
        """ Returns probability to generate new code. 
        
        Returns:
            Ratio of succesful to total generation tries
        """
        return float(self.nr_new) / self.nr_tries


class CodeMiner():
    """ Mines operator implementations using GPT-3 Codex. """
    
    def __init__(self, operators, synthesizer, nr_levels=11, max_samples=10):
        """ Initializes for given synthesizer.
        
        Args:
            operators: keeps track of generated operators
            synthesizer: used to generate operator code
            nr_levels: how many temperature levels to consider
            max_samples: try to limit to this number of samples
        """
        self.operators = operators
        self.synthesizer = synthesizer
        self.nr_levels = nr_levels
        self.max_samples = max_samples
        temperature_delta = 1.0 / (nr_levels-1)
        self.logger = logging.getLogger('all')
        self.logger.info(f'Temperature Delta: {temperature_delta}')
        self.temperatures = [temperature_delta * s for s in range(nr_levels)]
        self.logger.info(f'Temperatures Considered: {self.temperatures}')
        self.temp2stats = defaultdict(lambda:TemperatureStats())
    
    def mine(self, task):
        """ Mine code for given generation task.
        
        Args:
            task: describes code generation task
        
        Returns:
            ID of generated code in operator library (None if unsuccessful)
        """
        self.logger.info(f'Mining code for task: {task}')
        t2samples = self._optimized_samples(task)
        self.logger.info(f'Optimized Sample Counts: {t2samples}')
        code, temp = self._sample(task, t2samples)
        self.logger.info(f'Mined Code with Temperature {temp}:\n{code}')
        task_id = task['task_id']
        return self.operators.add_op(task_id, code, temp)
    
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
        temps = list(t2samples.keys())
        temps.sort()
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
        if not self.temp2stats:
            for tmp_idx in [1, self.nr_levels/2, self.nr_levels-1]:
                temperature = self.temperatures[tmp_idx]
                code = self.synthesizer.generate(task, temperature)
                if self.operators.is_known(code):
                    self._update_stats(temperature, False)
                else:
                    self._update_stats(temperature, True)
        
        x = [0]
        y = [0]
        for temperature in self.temperatures:
            if temperature in self.temp2stats:
                stats = self.temp2stats[temperature]
                x += [temperature]
                y += [stats.new_ratio()]
        
        self.logger.info(f'Fitting Vector: {y}')
        x = np.array(x).reshape((-1, 1))
        y = np.array(y)
        model = sklearn.linear_model.LinearRegression()
        model.fit(x, y)
        self.logger.debug(f'Model: {model}')
        return model
    
    def _optimized_samples(self, task):
        """ Optimize the distribution of samples over temperatures.
        
        Args:
            task: describes code generation task
        
        Returns:
            dictionary mapping temperatures to sample counts
        """
        task_id = task['task_id']
        if self.operators.get_ids(task_id):
            model = self._model(task)
            t2samples = Counter()
            for _ in range(self.max_samples):
                expansions = []
                for temp in self.temperatures[1:]:
                    t2samples_c = t2samples.copy()
                    t2samples_c.update([temp])
                    e_min = self._e_min_temp(t2samples_c, model)
                    expansions += [(t2samples_c, e_min)]
                self.logger.debug(f'Sample expansions: {expansions}')
                t2samples = min(expansions, key=lambda c_e:c_e[1])[0]
            return t2samples
        else:
            return {0.0:1}
    
    def _p_new(self, nr_t_samples, temperature, model):
        """ Calculates probability of retrieving new code.
        
        Args:
            nr_t_samples: number of code samples for temperature
            temperature: draw samples at this temperature
            model: predicts new code probability, given temperature
        
        Returns:
            probability that new code is generated at least once
        """
        temperature = np.array(temperature).reshape((-1, 1))
        p_per_sample = model.predict(temperature)
        p_per_sample = max(p_per_sample, 0.0)
        p_per_sample = min(p_per_sample, 1.0)
        self.logger.debug(f'p_per_sample: {p_per_sample}')
        p_per_sample_n = 1.0 - p_per_sample
        p_n = p_per_sample_n ** nr_t_samples
        self.logger.debug(f'p_n: {p_n}')
        p = 1.0 - p_n
        self.logger.debug(f'P(New | {temperature}) = {p}')
        return p
    
    def _sample(self, task, t2samples):
        """ Execute sample schedule and return first novel code.
        
        Args:
            task: describes code generation task
            t2samples: maps temperatures to sample counts
        
        Returns:
            unknown code and associated temperature
        """
        for temp in self.temperatures:
            t_samples = t2samples[temp]
            for _ in range(t_samples):
                code = self.synthesizer.generate(task, temp)
                if not self.operators.is_known(code):
                    self._update_stats(temp, True)
                    return code, temp
                else:
                    self._update_stats(temp, False)
        
        while True:
            code = self.synthesizer.generate(task, 1)
            if not self.operators.is_known(code):
                self._update_stats(1.0, True)
                return code, 1.0
            else:
                self._update_stats(1.0, False)
    
    def _update_stats(self, temperature, success):
        """ Updates temperature-related statistics.
        
        Args:
            temperature: update statistics on this temperature
            success: True iff mining new code was successful
        """
        stats = self.temp2stats[temperature]
        stats.nr_tries += 1
        if success:
            stats.nr_new += 1