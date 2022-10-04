'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
from collections import defaultdict
import gym.spaces
import logging
import numpy as np
import random
import stable_baselines3.a2c


class MiningEnv(gym.Env):
    """ Models decisions related to code mining temperature. """
    
    def __init__(self, operators, synthesizer, nr_levels, nr_samples):
        """ Initializes for given synthesizer.
        
        Args:
            operators: keeps track of generated operators
            synthesizer: used to generate operator code
            nr_levels: how many temperature levels to consider
            nr_samples: try to limit to this number of samples
        """
        gym.Env.__init__(self)
        self.logger = logging.getLogger('all')
        self.operators = operators
        self.synthesizer = synthesizer
        self.nr_levels = nr_levels
        self.nr_samples = nr_samples
        temperature_delta = 1.0 / nr_levels
        self.logger.debug(f'Temperature Delta: {temperature_delta}')
        self.temperatures = [
            temperature_delta * s for s in range(1, nr_levels+1)]
        self.logger.info(f'Temperatures Considered: {self.temperatures}')
        self.action_space = gym.spaces.Box(
            low=0, high=1, shape=(nr_levels,), 
            dtype=np.uint8)
        self.observation_space = gym.spaces.Box(
            low=0, high=1, shape=(2,),
            dtype=np.uint8)
        self.task = None
        self.taskid2c_t = defaultdict(lambda:[])
    
    def pop_code(self, task_id):
        """ Get code with lowest temperature seen so far and reset.
        
        Args:
            task_id: get code for this task ID
        
        Returns:
            tuple: newly generated code and associated temperature
        """
        mined = self.taskid2c_t[task_id]
        mined.sort(key=lambda c_t:c_t[1])
        c_t = mined[0]
        del self.taskid2c_t[task_id]
        return c_t
    
    def reset(self):
        """ Returns vector of observations (nothing else to do). """
        return self._observe()
    
    def step(self, action):
        """ Mines code using strategy described by action.
        
        Args:
            action: describes number of samples per temperature level
        
        Returns:
            observation, reward, termination, meta-data
        """
        t2samples= {}
        for idx, temp in enumerate(self.temperatures):
            t_samples = round(action[idx] * self.nr_samples)
            t2samples[temp] = t_samples
        self.logger.info(f'#Samples per Temperature: {t2samples}')
        
        code, temp = self._sample(t2samples)
        self.logger.info(f'Mined Code with Temperature {temp}:\n{code}')
        task_id = self.task['task_id']
        self.taskid2c_t[task_id] += [(code, temp)]
        reward = 1.0 - temp
        
        return self._observe(), reward, True, {}
    
    def _observe(self):
        """ Generates observation for RL algorithm.
        
        Returns:
            array with observation values (prompt size, #implementations) 
        """
        prompt_path = self.task['template']
        prompt = self.synthesizer.load_prompt(prompt_path, {})
        prompt_size = len(prompt)
        scaled_size = float(prompt_size) / 500
        assert scaled_size <= 1.0
        
        task_id = self.task['task_id']
        op_ids = self.operators.get_ids(task_id)
        nr_operators = len(op_ids)
        scaled_nr = float(min(nr_operators, 10)) / 10
        
        return np.array([scaled_size, scaled_nr])
    
    def _sample(self, t2samples):
        """ Execute sample schedule and return first novel code.
        
        Args:
            t2samples: maps temperatures to sample counts
        
        Returns:
            unknown code and associated temperature
        """
        for temp in self.temperatures:
            t_samples = t2samples[temp]
            for _ in range(t_samples):
                code = self.synthesizer.generate(self.task, temp)
                if not self.operators.is_known(code):
                    return code, temp
        
        while True:
            code = self.synthesizer.generate(self.task, 1)
            if not self.operators.is_known(code):
                return code, 1.0


class CodeMiner():
    """ Mines code using reinforcement learning for configuration. """
    
    def __init__(self, operators, synthesizer, nr_levels=4, nr_samples=10):
        """ Initializes for given synthesizer.
        
        Args:
            operators: keeps track of generated operators
            synthesizer: used to generate operator code
            nr_levels: how many temperature levels to consider
            nr_samples: try to limit to this number of samples
        """
        self.logger = logging.getLogger('all')
        self.operators = operators
        self.synthesizer = synthesizer
        
        self.env = MiningEnv(operators, synthesizer, nr_levels, nr_samples)
        self.logger.info(f'Mining Environment: {self.env}')
        self.agent = stable_baselines3.a2c.A2C(
            'MlpPolicy', self.env, 
            n_steps=2, normalize_advantage=True)
    
    def mine(self, task):
        """ Mine code as specified in given generation task.
        
        Args:
            task: describes code generation task
        
        Returns:
            ID of newly generated code in operator library
        """
        task_id = task['task_id']
        if self.operators.get_ids(task_id):
            # self.env.task = task
            # self.agent.learn(1)
            # code, temperature = self.env.pop_code(task_id)
            # return self.operators.add_op(task_id, code, temperature)
            temperature = random.random()
            code = self.synthesizer.generate(task, temperature)
            self.logger.info(f'Mined first implementation for task {task_id}')
            return self.operators.add_op(task_id, code, temperature)
        else:
            code = self.synthesizer.generate(task, 0.0)
            self.logger.info(f'Mined first implementation for task {task_id}')
            return self.operators.add_op(task_id, code, 0.0)


if __name__ == '__main__':
    miner = CodeMiner(None, None, 4, 10)