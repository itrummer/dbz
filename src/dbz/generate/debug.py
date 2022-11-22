'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
from collections import Counter
import logging


class Debugger():
    """ Traces unsolved checks based to faulty operator implementations. """
    
    def __init__(self, composer):
        """ Initializes with given composer. 
        
        Args:
            composer: composes the SQL execution engine
        """
        self.composer = composer
        self.logger = logging.getLogger('all')
    
    def to_redo(self):
        """ Suggests generation task to redo and corresponding context. 
        
        Returns:
            ranked list of pairs (task ID, probability)
        """
        failure_info = self.composer.failure_info()
        self.logger.debug(f'Failure Info: {failure_info}')
        
        # Calculate marginal probability of unsolved tasks using Bayes formula:
        # P(No Operator | Passes) ~ P(Passes | No Operator) * P(No Operator)
        nr_passed = self._nr_passed_checks(failure_info.passed_checks)
        self.logger.info(f'Number of passed checks: {nr_passed}')
        nr_implementations = failure_info.task2nr_ops
        self.logger.info(f'Number of implementations: {nr_implementations}')
        
        failed_checks = failure_info.failed_checks
        assert len(failed_checks) == 1
        redo_candidates = failed_checks[0]['requirements']
        task2p_unsolved = {}
        for task_id in redo_candidates:
            p_unsolved = self._p_unsolved(
                nr_passed, nr_implementations, task_id)
            task2p_unsolved[task_id] = p_unsolved
        
        self.logger.info(f'Tasks and redo weights: {task2p_unsolved}')
        tasks_weights = list(task2p_unsolved.items())
        tasks_weights.sort(key=lambda t_w:t_w[1], reverse=True)
        self.logger.info(f'Tasks and weights by priority: {tasks_weights}')
        return tasks_weights
    
    def _nr_passed_checks(self, passed_checks):
        """ Calculates number of passed checks per task. 
        
        Args:
            passed_checks: list of passed checks
        
        Returns:
            counter mapping task IDs to the number of passed checks
        """
        task2nr = Counter()
        for check in passed_checks:
            task2nr.update(check['requirements'])
        
        return task2nr
    
    def _p_unsolved(self, nr_checks, nr_implementations, task_id):
        """ Calculates probability that task is unsolved. 
        
        Args:
            nr_checks: number of checks passed per task pre-failure
            nr_implementations: number of implementations per task pre-failure
            task_id: calculate probability that this task is unsolved
        
        Returns:
            probability that no correct code is available for task
        """
        p_incorrect_code = 0.9 ** nr_checks[task_id]
        p_unsolved = p_incorrect_code ** nr_implementations[task_id]
        self.logger.debug(f'*** Task_ID: {task_id} - P_unsolved: {p_unsolved}')
        self.logger.debug(f'#checks: {nr_checks[task_id]}')
        self.logger.debug(f'#implementations: {nr_implementations[task_id]}')
        self.logger.debug(f'p_incorrect_code: {p_incorrect_code}')
        return p_unsolved