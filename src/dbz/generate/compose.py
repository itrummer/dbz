'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
from collections import defaultdict
from dataclasses import dataclass
import dbz.execute.check
import dbz.execute.engine
import logging


@dataclass
class FailureInfo():
    """ Contains helpful information for debugging. """
    failed_task_id: str
    checks_at_fail: list
    passes_at_fail: list
    nr_failed_ops: int
    prior_comps: list
    prior_checks: list


class OldComposer():
    """ Composes operator implementations into full SQL engine. """
    
    def __init__(self, config, operators, tasks):
        """ Initialize with operator manager. 
        
        Args:
            config: JSON file configuring synthesis
            operators: manages operator implementations
            tasks: manages generation tasks and checks
        """
        self.logger = logging.getLogger('all')
        self.ops = operators
        self.tasks = tasks
        self.task_order = [t['task_id'] for t in tasks.gen_tasks]
        self.nr_tasks = len(self.task_order)
        self.last_task_idx = self.nr_tasks - 1
        self.idx2checks = self._schedule_checks()
        self.idx2passes = defaultdict(lambda:[])
        self.compositions = defaultdict(lambda:[])
        self.compositions[-1] = [{}]
        
        sql_ref_info = config['sql_ref']
        pg_db = sql_ref_info['pg_db']
        pg_user = sql_ref_info['pg_user']
        pg_pwd = sql_ref_info['pg_pwd']
        pg_host = sql_ref_info['host']
        self.sql_ref = dbz.execute.engine.PgEngine(
            pg_db, pg_user, pg_pwd, pg_host)
        
        test_access = config['test_access']
        data_dir = test_access['data_dir']
        self.paths = dbz.util.DbzPaths(data_dir)
        self.python = test_access['python']
        
        code_ref_info = config['code_ref']
        ref_path = code_ref_info['ref_operators']
        with open(ref_path) as file:
            ref_lib = file.read()
        self.code_ref = dbz.execute.engine.DbzEngine(
            self.paths, ref_lib, self.python)
    
    def failure_info(self):
        """ Returns information on composition failure reasons. 
        
        Returns:
            helpful information to debug failure
        """
        for task_idx in range(self.nr_tasks):
            if not self.compositions[task_idx]:
                task_id = self.task_order[task_idx]
                checks_at_fail = self.idx2checks[task_idx]
                passes_at_fail = self.idx2passes[task_idx]
                nr_failed_ops = len(self.ops.get_ids(task_id))
                prior_comps = self.compositions[task_idx-1]
                prior_checks = [
                    c for i in range(task_idx) 
                    for c in self.idx2checks[i]]
                failure_info = FailureInfo(
                    task_id, checks_at_fail, 
                    passes_at_fail, nr_failed_ops, 
                    prior_comps, prior_checks)
                self.logger.info(f'Failure Info ({task_id}): {failure_info}')
                return failure_info
        
        return None
    
    def finished(self):
        """ Checks whether a complete engine was generated. 
        
        Returns:
            True if a working SQL engine was generated
        """
        return self.compositions[self.last_task_idx]
    
    def final_code(self):
        """ Retrieves code for complete SQL engine. 
        
        Call only after composition is finished!
        
        Returns:
            Code implementing operators of SQL execution engine
        """
        final_compositions = self.compositions[self.last_task_idx]
        final_composition = final_compositions[0]
        return self._composition_code(final_composition)
    
    def update(self, updated_task, new_code_id):
        """ Update compositions using new implementation. 
        
        Args:
            updated_task: new implementation for this task
            new_code_id: ID of new code for updated task
        """
        updated_idx = self.task_order.index(updated_task)
        last_result = self.compositions[updated_idx-1]
        
        for task_idx in range(updated_idx, self.nr_tasks):
            updated = (task_idx == updated_idx)
            task = self.task_order[task_idx]
            cur_code_ids = [new_code_id] if updated else self.ops.get_ids(task)
            
            next_result = []
            for last_row in last_result:
                for cur_code_id in cur_code_ids:
                    next_row = last_row.copy()
                    next_row[task] = cur_code_id
                    next_result += [next_row]
        
            self.logger.debug(f'Updating at {task_idx}, next result: {next_result}')
            last_result = self._filter(next_result, task_idx)
            self.logger.debug(f'Updating at {task_idx}, last result: {last_result}')
            self.compositions[task_idx] += last_result
    
    def _applicable_checks(self, tasks):
        """ Retrieves applicable checks, given finished tasks.
        
        Args:
            tasks: list of finished tasks
        
        Returns:
            set of applicable check IDs
        """
        tasks_set = set(tasks)
        applicable = set()
        for check_idx, check in enumerate(self.tasks.check_tasks):
            required_set = set(check['requirements'])
            if required_set.issubset(tasks_set):
                applicable.add(check_idx)
        return applicable
    
    def _cache_get(self, composition, check):
        """ Retrieves check result from cache if available.
        
        Args:
            composition: maps task IDs to code IDs
            check: retrieve from result cache of this check
        
        Returns:
            Boolean result if cached, None otherwise
        """
        if 'cache' in check:
            cache_key = self._get_key(composition, check)
            cache = check['cache']
            return cache.get(cache_key)
        else:
            return None
    
    def _cache_put(self, composition, check, passed):
        """ Updates cache storing check results.
        
        Args:
            composition: maps task IDs to code IDs
            check: cache result for this check
            passed: whether check was passed or not
        """
        if 'cache' not in check:
            check['cache'] = {}
        
        cache_key = self._get_key(composition, check)
        check['cache'][cache_key] = passed
    
    def _check(self, composition, check):
        """ Apply check to given composition. 
        
        Args:
            composition: maps tasks to selected implementations
            check: a test case for the given composition
        
        Returns:
            True iff the composition passes the check
        """
        if self._cache_get(composition, check) is None:
            library = self._composition_code(composition)
            test_engine = dbz.execute.engine.DbzEngine(
                self.paths, library, self.python)
            
            validator = dbz.execute.check.Validator(
                self.paths, [check], self.sql_ref, self.code_ref)
            passed = validator.validate(test_engine)
            self._cache_put(composition, check, passed)
        
        return self._cache_get(composition, check)
    
    def _composition_code(self, composition):
        """ Translates composition into a piece of code.
        
        Args:
            composition: maps tasks to code IDs
        
        Returns:
            a piece of Python code
        """
        parts = []
        for task, code_id in composition.items():
            code = self.ops.get_ops(task)[code_id][0]
            parts += [code]
        return '\n\n'.join(parts)
    
    def _filter(self, filter_in, task_idx):
        """ Filter result tuples via newly applicable predicates.
        
        Args:
            filter_in: filter input (a list of compositions)
            task_idx: filtering results for this task index
        
        Returns:
            list of tuples satisfying all predicates
        """
        checks = self.idx2checks[task_idx]
        passes = []
        filter_out = []
        for comp in filter_in:
            comp_passes = []
            for check in checks:
                comp_pass = self._check(comp, check)
                comp_passes += [comp_pass]
                                
            if all(comp_passes):
                filter_out += [comp]
            
            passes += [comp_passes]
        
        self.idx2passes[task_idx] += passes
        return filter_out
    
    def _get_key(self, composition, check):
        """ Calculates composition key used for check result caching. 
        
        Args:
            composition: maps task IDs to code IDs
            check: calculate key for this check's cache
        
        Returns:
            a frozen set capturing composition aspects relevant for check 
        """
        sub_comp = {}
        for req_id in check['requirements']:
            code_id = composition[req_id]
            sub_comp[req_id] = code_id
        
        return frozenset(sub_comp.items())
    
    def _schedule_checks(self):
        """ Schedule checks based on task order. 
        
        Returns:
            dictionary mapping task indexes to list of checks
        """
        idx2checks = {}
        for task_idx in range(self.nr_tasks):
            prior_tasks = [self.task_order[i] for i in range(task_idx)]
            next_tasks = [self.task_order[i] for i in range(task_idx+1)]
            prior_check_ids = self._applicable_checks(prior_tasks)
            next_check_ids = self._applicable_checks(next_tasks)
            new_check_ids = next_check_ids - prior_check_ids
            new_checks = [self.tasks.check_tasks[i] for i in new_check_ids]
            idx2checks[task_idx] = new_checks
        
        self.logger.info(f'Scheduled checks: {idx2checks}')
        return idx2checks


class Composer():
    """ Composes operator implementations into full SQL engine. """
    
    def __init__(self, config, operators, tasks):
        """ Initialize with operator manager. 
        
        Args:
            config: JSON file configuring synthesis
            operators: manages operator implementations
            tasks: manages generation tasks and checks
        """
        self.logger = logging.getLogger('all')
        self.ops = operators
        self.tasks = tasks
        self.task_order = [t['task_id'] for t in tasks.gen_tasks]
        self.nr_tasks = len(self.task_order)
        self.idx2checks = self._schedule_checks()
        self.idx2passes = defaultdict(lambda:[])
        self.composition = {tid:0 for tid in self.task_order}
        self.works_until = -1
        
        sql_ref_info = config['sql_ref']
        pg_db = sql_ref_info['pg_db']
        pg_user = sql_ref_info['pg_user']
        pg_pwd = sql_ref_info['pg_pwd']
        pg_host = sql_ref_info['host']
        self.sql_ref = dbz.execute.engine.PgEngine(
            pg_db, pg_user, pg_pwd, pg_host)
        
        test_access = config['test_access']
        data_dir = test_access['data_dir']
        self.paths = dbz.util.DbzPaths(data_dir)
        self.python = test_access['python']
        
        code_ref_info = config['code_ref']
        ref_path = code_ref_info['ref_operators']
        with open(ref_path) as file:
            ref_lib = file.read()
        self.code_ref = dbz.execute.engine.DbzEngine(
            self.paths, ref_lib, self.python)
    
    def failure_info(self):
        """ Returns information on composition failure reasons. 
        
        Returns:
            helpful information to debug failure (or None if no failure)
        """
        fail_idx = self.works_until + 1
        if fail_idx < self.nr_tasks:
            task_id = self.task_order[fail_idx]
            checks_at_fail = self.idx2checks[fail_idx]
            passes_at_fail = self.idx2passes[fail_idx]
            nr_failed_ops = len(self.ops.get_ids(task_id))
            prior_comp = self.composition.copy()
            for next_idx in range(fail_idx, self.nr_tasks):
                task_idx = self.task_order[next_idx]
                del prior_comp[task_idx]
            prior_comps = [prior_comp]
            prior_checks = [
                c for i in range(fail_idx) 
                for c in self.idx2checks[i]]
            failure_info = FailureInfo(
                task_id, checks_at_fail, 
                passes_at_fail, nr_failed_ops, 
                prior_comps, prior_checks)
            self.logger.debug(
                f'Failure Info ({task_id}): {failure_info}')
            return failure_info
        else:
            return None
    
    def finished(self):
        """ Checks whether a complete engine was generated. 
        
        Returns:
            True if a working SQL engine was generated
        """
        return self.works_until == self.nr_tasks - 1
    
    def final_code(self):
        """ Retrieves code for complete SQL engine. 
        
        Call only after composition is finished!
        
        Returns:
            Code implementing operators of SQL execution engine
        """
        assert self.finished(), 'No valid engine generated yet'
        return self._composition_code(self.composition)
    
    def update(self, updated_task_id, new_code_id):
        """ Try new code candidate to improve current composition. 
        
        Args:
            updated_task_id: new implementation for this task
            new_code_id: ID of new code for updated task
        """
        updated_idx = self.task_order.index(updated_task_id)
        candidate_comp = self.composition.copy()
        candidate_comp[updated_task_id] = new_code_id
        
        candidate_until = updated_idx - 1
        for task_idx in range(updated_idx, self.nr_tasks):
            if self._filter([candidate_comp], task_idx):
                candidate_until = task_idx
            else:
                break

        self.logger.info(f'Candidate works until {candidate_until}')
        if candidate_until > self.works_until:
            self.logger.info(f'Replacing prior operator')
            self.works_until = candidate_until
            self.composition = candidate_comp
    
    def _applicable_checks(self, tasks):
        """ Retrieves applicable checks, given finished tasks.
        
        Args:
            tasks: list of finished tasks
        
        Returns:
            set of applicable check IDs
        """
        tasks_set = set(tasks)
        applicable = set()
        for check_idx, check in enumerate(self.tasks.check_tasks):
            required_set = set(check['requirements'])
            if required_set.issubset(tasks_set):
                applicable.add(check_idx)
        return applicable
    
    def _cache_get(self, composition, check):
        """ Retrieves check result from cache if available.
        
        Args:
            composition: maps task IDs to code IDs
            check: retrieve from result cache of this check
        
        Returns:
            Boolean result if cached, None otherwise
        """
        if 'cache' in check:
            self.logger.info('Retrieved check result from cache')
            cache_key = self._get_key(composition, check)
            cache = check['cache']
            return cache.get(cache_key)
        else:
            self.logger.info('No cached check result found')
            return None
    
    def _cache_put(self, composition, check, passed):
        """ Updates cache storing check results.
        
        Args:
            composition: maps task IDs to code IDs
            check: cache result for this check
            passed: whether check was passed or not
        """
        if 'cache' not in check:
            check['cache'] = {}
        
        cache_key = self._get_key(composition, check)
        check['cache'][cache_key] = passed
    
    def _check(self, composition, check):
        """ Apply check to given composition. 
        
        Args:
            composition: maps tasks to selected implementations
            check: a test case for the given composition
        
        Returns:
            True iff the composition passes the check
        """
        if self._cache_get(composition, check) is None:
            library = self._composition_code(composition)
            test_engine = dbz.execute.engine.DbzEngine(
                self.paths, library, self.python)
            
            validator = dbz.execute.check.Validator(
                self.paths, [check], self.sql_ref, self.code_ref)
            passed = validator.validate(test_engine)
            self._cache_put(composition, check, passed)
        
        return self._cache_get(composition, check)
    
    def _composition_code(self, composition):
        """ Translates composition into a piece of code.
        
        Args:
            composition: maps tasks to code IDs
        
        Returns:
            a piece of Python code
        """
        parts = []
        for task, code_id in composition.items():
            code = self.ops.get_ops(task)[code_id][0]
            parts += [code]
        return '\n\n'.join(parts)
    
    def _filter(self, filter_in, task_idx):
        """ Filter result tuples via newly applicable predicates.
        
        Args:
            filter_in: filter input (a list of compositions)
            task_idx: filtering results for this task index
        
        Returns:
            list of tuples satisfying all predicates
        """
        checks = self.idx2checks[task_idx]
        nr_checks = len(checks)
        passes = []
        filter_out = []
        for comp in filter_in:
            comp_passes = []
            for check_idx, check in enumerate(checks, 1):
                self.logger.info(
                    f'Check {check_idx}/{nr_checks} for task {task_idx}')
                comp_pass = self._check(comp, check)
                comp_passes += [comp_pass]
                                
            if all(comp_passes):
                filter_out += [comp]
            
            passes += [comp_passes]
        
        self.idx2passes[task_idx] += passes
        return filter_out
    
    def _get_key(self, composition, check):
        """ Calculates composition key used for check result caching. 
        
        Args:
            composition: maps task IDs to code IDs
            check: calculate key for this check's cache
        
        Returns:
            a frozen set capturing composition aspects relevant for check 
        """
        sub_comp = {}
        for req_id in check['requirements']:
            code_id = composition[req_id]
            sub_comp[req_id] = code_id
        
        return frozenset(sub_comp.items())
    
    def _schedule_checks(self):
        """ Schedule checks based on task order. 
        
        Returns:
            dictionary mapping task indexes to list of checks
        """
        idx2checks = {}
        for task_idx in range(self.nr_tasks):
            prior_tasks = [self.task_order[i] for i in range(task_idx)]
            next_tasks = [self.task_order[i] for i in range(task_idx+1)]
            prior_check_ids = self._applicable_checks(prior_tasks)
            next_check_ids = self._applicable_checks(next_tasks)
            new_check_ids = next_check_ids - prior_check_ids
            new_checks = [self.tasks.check_tasks[i] for i in new_check_ids]
            idx2checks[task_idx] = new_checks
        
        self.logger.info(f'Scheduled checks: {idx2checks}')
        return idx2checks