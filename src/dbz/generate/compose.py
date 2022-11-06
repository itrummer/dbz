'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
from dataclasses import dataclass
import dbz.execute.check
import dbz.execute.engine
import logging
import os.path


@dataclass
class FailureInfo():
    """ Contains helpful information for debugging. """
    passed_checks: list
    failed_checks: list
    task2nr_ops: dict


class Composer():
    """ Composes operator implementations into full SQL engine. """
    
    def __init__(self, config, operators, tasks, pre_code):
        """ Initialize with operator manager. 
        
        Args:
            config: JSON file configuring synthesis
            operators: manages operator implementations
            tasks: manages generation tasks and checks
            pre_code: code prefix
        """
        self.logger = logging.getLogger('all')
        self.ops = operators
        self.tasks = tasks
        self.pre_code = pre_code
        self.task_order = [t['task_id'] for t in tasks.gen_tasks]
        self.nr_tasks = len(self.task_order)
        self.idx2checks = self._schedule_checks()
        self.logger.info(f'Checking Schedule: {self.idx2checks}')
        self.composition = {tid:0 for tid in self.task_order}
        self.works_until = -1
        self.failure_info = None
        self.nr_validations = 0
        
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
        
        self.validator = dbz.execute.check.Validator(
            self.paths, self.sql_ref)        
    
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
        #assert self.finished(), 'No valid engine generated yet'
        return self._composition_code(self.composition)
    
    def update(self, updated_task_id, new_code_id):
        """ Try new code candidate to improve current composition. 
        
        Args:
            updated_task_id: new implementation for this task
            new_code_id: ID of new code for updated task
        
        Returns:
            True if the update resolved previous problems
        """
        updated_idx = self.task_order.index(updated_task_id)
        candidate_comp = self.composition.copy()
        candidate_comp[updated_task_id] = new_code_id
        
        if not self._old_checks(candidate_comp, updated_idx):
            return False
        
        passed_checks = []
        failed_checks = []
        candidate_until = self.works_until
        for task_idx in range(self.works_until+1, self.nr_tasks):
            checks = self.idx2checks[task_idx]
            all_passed = True
            for check in checks:
                self.logger.info(
                    f'Checking generation task {task_idx}/{self.nr_tasks} ...')
                if self._check(candidate_comp, check):
                    passed_checks += [check]
                else:
                    failed_checks += [check]
                    all_passed = False
                    break

            if all_passed:
                candidate_until = task_idx
            else:
                break

        self.logger.info(f'Candidate works until {candidate_until}')
        if candidate_until > self.works_until:
            self.logger.info(f'Replacing prior operator')
            self.works_until = candidate_until
            self.composition = candidate_comp
            
            if not self.finished():
                task2nr_ops = {}
                for task_id in self.task_order:
                    nr_ops = len(self.ops.get_ids(task_id))
                    task2nr_ops[task_id] = nr_ops

                self.failure_info = FailureInfo(
                    passed_checks, failed_checks, 
                    task2nr_ops)
            
            return True
        else:
            return False
    
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
            
            min_comp = {}
            for task_id in check['requirements']:
                code_id = composition[task_id]
                min_comp[task_id] = code_id
            library = self._composition_code(min_comp)
            test_engine = dbz.execute.engine.DbzEngine(
                self.paths, library, self.python)
            
            if 'query' in check:
                sql = check['query']
                self.logger.info(f'Checking query {sql} ...')
                code = test_engine.sql2code(sql, 'dummy')
            else:
                file_name = check['file']
                self.logger.info(f'Checking code {file_name} ...')
                query_code = check['code']
                code = test_engine.add_context(query_code, 'dummy')
            
            code_name = f'CodeV{self.nr_validations}.py'
            code_path = os.path.join(self.paths.tmp_dir, code_name)
            self.logger.info(f'Writing validated code to {code_path}')
            with open(code_path, 'w') as file:
                file.write(code)
            
            passed = self.validator.validate(test_engine, check)
            self._cache_put(composition, check, passed)
            self.nr_validations += 1
        
        return self._cache_get(composition, check)
    
    def _composition_code(self, composition):
        """ Translates composition into a piece of code.
        
        Args:
            composition: maps tasks to code IDs
        
        Returns:
            a piece of Python code
        """
        parts = [self.pre_code]
        for task_id, code_id in composition.items():
            code = self.ops.get_ops(task_id)[code_id][0]
            parts += [code]
        return '\n\n'.join(parts)
    
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
    
    def _old_checks(self, candidate_comp, updated_idx):
        """ Re-perform checks for candidate composition passed by others.
        
        Args:
            candidate_comp: check candidate composition
            updated_idx: index of updated operator in generation order
            
        Returns:
            True iff all old checks are passed with new implementation
        """
        old_checks = []
        for idx in range(updated_idx, self.works_until+2):
            old_checks += self.idx2checks[idx]
        old_checks.sort(key=lambda c:self._selectivity(c))
        nr_checks = len(old_checks)
        
        for idx, old_check in enumerate(old_checks, 1):
            self.logger.info(f'Performing old check {idx}/{nr_checks} ...')
            self.logger.info(
                f'Best composition works until ' +\
                f'task {self.works_until}/{self.nr_tasks}')
            if not self._check(candidate_comp, old_check):
                return False
        
        return True
    
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
            new_checks.sort(key=lambda c:len(c['requirements']))
            idx2checks[task_idx] = new_checks
        
        self.logger.info(f'Scheduled checks: {idx2checks}')
        return idx2checks
    
    def _selectivity(self, check):
        """ Calculates selectivity of check using cache content.
        
        Args:
            check: estimate probability to pass this check
        
        Returns:
            a selectivity number between 0 and 1 (default: 0.5)
        """
        if 'cache' in check:
            comp2result = check['cache']
            nr_checked = len(comp2result)
            nr_passed = sum(comp2result.values())
            return float(nr_passed) / nr_checked
        else:
            return 0.5