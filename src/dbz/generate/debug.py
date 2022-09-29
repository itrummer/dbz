'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
from collections import Counter
from collections import defaultdict
import random


class Debugger():
    """ Traces unsolved checks based to faulty operator implementations. """
    
    def __init__(self, composer):
        """ Initializes with given composer. 
        
        Args:
            composer: composes the SQL execution engine
        """
        self.composer = composer
    
    def to_redo(self):
        """ Suggests generation task to redo. 
        
        Returns:
            ID of task to redo
        """
        failure_info = self.composer.failure_info()
        print(f'Failure Info: {failure_info}')
        groups = self._group_checks(
            failure_info.failed_checks,
            failure_info.failed_passes)
        group_reqs = []
        for group in groups:
            group_req = set([r for rs in group for r in rs['requirements']])
            group_reqs += [group_req]
        
        group_reqs.sort(key=lambda r:len(r))
        disjunct_reqs = []
        prior_reqs = set()
        for group_req in group_reqs:
            print(f'Group req: {group_req}; prior_reqs: {prior_reqs}')
            if not group_req & prior_reqs:
                disjunct_reqs += [group_req]
                prior_reqs.update(group_req)
        
        # Calculate marginal probability of unsolved tasks using Bayes formula:
        # P(No Operator | Passes) ~ P(Passes | No Operator) * P(No Operator)
        nr_checks = self._nr_checks(failure_info)
        nr_implementations = self._nr_implementations(failure_info)
        
        task2prob = {}
        for task_id in prior_reqs:
            p_passes = self._p_passes(
                disjunct_reqs, task_id)
            p_unsolved = self._p_unsolved(
                nr_checks, nr_implementations, 
                task_id)
            task2prob[task_id] = p_passes * p_unsolved
        
        todo_id = min(task2prob, key=task2prob.get)
        print(f'Selected task to redo: {todo_id}')
        return todo_id
            
    def _group_checks(self, checks, passes):
        """ Groups s.t. no composition satisfies all checks in any group.
        
        Args:
            checks: list of checks
            passes: per-composition passes
        
        Returns:
            list of groups (i.e., each group is represented as list of checks)
        """
        nr_checks = len(checks)
        no_passes = [True] * nr_checks
        for comp_passes in passes:
            for check_idx, passed in enumerate(comp_passes):
                no_passes[check_idx] &= not passed 
        
        groups = [checks]
        for check, no_pass in zip(checks, no_passes):
            if no_pass:
                groups += [[check]]
        
        return groups
    
    def _nr_checks(self, failure_info):
        """ Calculates number of checks per task before failure. 
        
        Args:
            failure_info: information on compositions before failure
        
        Returns:
            counter mapping task IDs to the number of checks
        """
        task2nr = Counter()
        for check in failure_info.prior_checks:
            task2nr.update(check['requirements'])
        
        failed_task_id = failure_info.failed_task_id
        task2nr[failed_task_id] = 0
        
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
        p_solved = 1.0 - p_incorrect_code ** nr_implementations[task_id]
        return 1.0 - p_solved