'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
from collections import Counter
from collections import defaultdict
import logging
import random


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
        """ Suggests generation task to redo. 
        
        Returns:
            ID of task to redo
        """
        failure_info = self.composer.failure_info()
        self.logger.debug(f'Failure Info: {failure_info}')
        passed_group, failed_groups = self._group_checks(
            failure_info.checks_at_fail,
            failure_info.passes_at_fail)
        group_reqs = []
        for group in failed_groups:
            group_req = set([r for rs in group for r in rs['requirements']])
            group_reqs += [group_req]
        
        group_reqs.sort(key=lambda r:len(r))
        disjunct_reqs = []
        prior_reqs = set()
        for group_req in group_reqs:
            self.logger.debug(
                f'Group req: {group_req}; prior_reqs: {prior_reqs}')
            if not group_req & prior_reqs:
                disjunct_reqs += [group_req]
                prior_reqs.update(group_req)
        
        # Calculate marginal probability of unsolved tasks using Bayes formula:
        # P(No Operator | Passes) ~ P(Passes | No Operator) * P(No Operator)
        failed_task_id = failure_info.failed_task_id
        passed_checks = passed_group + failure_info.prior_checks
        nr_checks = self._nr_checks(failed_task_id, passed_checks)
        nr_implementations = self._nr_implementations(failure_info)
        
        task2p_unsolved = {}
        for task_id in prior_reqs:
            p_passes = self._p_passes(
                disjunct_reqs, task_id)
            p_unsolved = self._p_unsolved(
                nr_checks, nr_implementations, 
                task_id)
            task2p_unsolved[task_id] = p_passes * p_unsolved
        
        self.logger.info(f'Tasks and redo weights: {task2p_unsolved}')
        choices = list(task2p_unsolved.keys())
        weights = task2p_unsolved.values()
        todo_id = random.choices(choices, weights=weights, k=1)[0]
        # todo_id = max(task2p_unsolved, key=task2p_unsolved.get)
        self.logger.info(f'Selected task to redo: {todo_id}')
        return todo_id
            
    def _group_checks(self, checks, passes):
        """ Divides checks into groups that passed/failed for all compositions.
        
        Args:
            checks: list of checks
            passes: per-composition passes
        
        Returns:
            one group of checks that passed, groups of checks that failed
        """
        nr_checks = len(checks)
        all_passes = [True] * nr_checks
        no_passes = [True] * nr_checks
        for comp_passes in passes:
            for check_idx, passed in enumerate(comp_passes):
                all_passes[check_idx] &= passed
                no_passes[check_idx] &= not passed 

        failed_groups = [checks]
        passed_groups = []
        for check, all_pass, no_pass in zip(
            checks, all_passes, no_passes):
            if all_pass:
                passed_groups += [check]
            if no_pass:
                failed_groups += [[check]]
        
        return passed_groups, failed_groups
    
    def _nr_checks(self, failed_task_id, passed_checks):
        """ Calculates number of checks per task before failure. 
        
        Args:
            failed_task_id: ID of failed task
            passed_checks: list of passed checks
        
        Returns:
            counter mapping task IDs to the number of checks
        """
        task2nr = Counter()
        task2nr[failed_task_id] = 0
        for check in passed_checks:
            task2nr.update(check['requirements'])
        
        return task2nr
    
    def _nr_implementations(self, failure_info):
        """ Calculates number of implementations per task before failure. 
        
        Args:
            failure_info: information about failure
        
        Returns:
            dictionary mapping task IDs to the number of implementations
        """
        task2code = defaultdict(lambda:set())
        for comp in failure_info.prior_comps:
            for task_id, code_id in comp.items():
                task2code[task_id].add(code_id)
        
        task2nr = {t:len(c) for t, c in task2code.items()}
        failed_task_id = failure_info.failed_task_id
        nr_failed_ops = failure_info.nr_failed_ops
        task2nr[failed_task_id] = nr_failed_ops
        
        return task2nr
    
    def _p_passes(self, disjunct_reqs, unsolved_task_id):
        """ Calculates probability to fail checks, given unsolved task.
        
        Args:
            disjunct_reqs: list of disjunct requirement sets
            unsolved_task_id: assume this task is unsolved
        
        Returns:
            probability (float between 0 and 1)
        """
        prob = 1.0
        for reqs in disjunct_reqs:
            if unsolved_task_id not in reqs:
                p_pass = 1.0
                for task_id in reqs:
                    p_solved = 1.0 - self._p_unsolved(task_id)
                    p_pass *= p_solved
                prob *= 1.0 - p_pass
        
        self.logger.debug(f'Task_ID: {unsolved_task_id}; P(Passes): {prob}')
        return prob
    
    def _p_unsolved(self, nr_checks, nr_implementations, task_id):
        """ Calculates probability that task is unsolved. 
        
        Args:
            nr_checks: number of checks passed per task pre-failure
            nr_implementations: number of implementations per task pre-failure
            task_id: calculate probability that this task is unsolved
        
        Returns:
            probability that no correct code is available for task
        """
        p_incorrect_code = 0.5 ** nr_checks[task_id]
        p_unsolved = p_incorrect_code ** nr_implementations[task_id]
        self.logger.debug(f'*** Task_ID: {task_id} - P_unsolved: {p_unsolved}')
        self.logger.debug(f'#checks: {nr_checks[task_id]}')
        self.logger.debug(f'#implementations: {nr_implementations[task_id]}')
        self.logger.debug(f'p_incorrect_code: {p_incorrect_code}')
        return p_unsolved