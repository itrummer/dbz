'''
Created on Sep 25, 2022

@author: immanueltrummer
'''
from dataclasses import dataclass
import dbz.analyze.component
import dbz.execute.check
import dbz.execute.engine
import logging
import os.path
import random
import time


@dataclass
class FailureInfo():
    """ Contains helpful information for debugging. """
    passed_checks: list
    failed_checks: list
    task2nr_ops: dict


class Composer(dbz.analyze.component.AnalyzedComponent):
    """ Composes operator implementations into full SQL engine. """
    
    def __init__(self, config, operators, tasks, pre_code, ablation=False):
        """ Initialize with operator manager. 
        
        Args:
            config: JSON file configuring synthesis
            operators: manages operator implementations
            tasks: manages generation tasks and checks
            pre_code: code prefix used for execution
            ablation: randomize test case order for ablation iff True
        """
        super().__init__()
        self.logger = logging.getLogger('all')
        self.ops = operators
        self.tasks = tasks
        self.pre_code = pre_code
        self.task_order = [t['task_id'] for t in tasks.gen_tasks]
        self.nr_tasks = len(self.task_order)
        self.fct2tid = {
            t['function_name']:t['task_id'] 
            for t in tasks.gen_tasks}
        self.logger.info(f'Function names to task IDs: {self.fct2tid}')
        self.idx2checks = self._schedule_checks()
        self.checks = [
            c for i in range(self.nr_tasks) 
            for c in self.idx2checks[i]]
        
        if ablation:
            self.logger.info('Shuffling checks for ablation ...')
            random.shuffle(self.checks)
        
        self.logger.info(f'Checks: {self.checks}')
        self.nr_checks = len(self.checks)
        self.composition = {tid:0 for tid in self.task_order}
        self.max_passed = -1
        self.passed_checks = []
        self.failed_checks = []
        self.nr_validations = 0
        
        sql_ref_info = config['sql_ref']
        pg_db = sql_ref_info['pg_db']
        pg_user = sql_ref_info['pg_user']
        pg_pwd = sql_ref_info['pg_pwd']
        pg_host = sql_ref_info['host']
        self.sql_ref = dbz.execute.engine.PgEngine(
            pg_db, pg_user, pg_pwd, pg_host, True)
        
        test_access = config['test_access']
        data_dir = test_access['data_dir']
        self.paths = dbz.util.DbzPaths(data_dir)
        self.python = test_access['python']
        
        self.validator = dbz.execute.check.Validator(self.paths, self.sql_ref)
    
    def all_code(self):
        """ Retrieves code for all operators. 
        
        Returns:
            Code implementing operators of SQL execution engine
        """
        return self._composition_code(self.composition)
    
    def call_history(self):
        """ Returns call history for this component and sub-components. 
        
        Returns:
            dictionary mapping sub-components to call logs
        """
        return {"composer":self.history, **self.validator.call_history()}
    
    def failure_info(self):
        """ Returns information on last failure. 
        
        Returns:
            failure info
        """
        task2nr_ops = {}
        for task_id in self.task_order:
            nr_ops = len(self.ops.get_ids(task_id))
            task2nr_ops[task_id] = nr_ops

        return FailureInfo(
            self.passed_checks, 
            self.failed_checks, 
            task2nr_ops)
    
    def finished(self):
        """ Checks whether a complete engine was generated. 
        
        Returns:
            True if a working SQL engine was generated
        """
        return self.max_passed >= self.nr_checks
    
    def update(self, updates, mode):
        """ Try new code candidate to improve current composition.
        
        Args:
            updates: maps task IDs to new code IDs
            mode: update mode ("force", "optional", "test")
        
        Returns:
            True if the update resolved previous problems
        """
        start_s = time.time()
        candidate = self.composition.copy()
        candidate.update(updates)
        
        if mode == 'force':
            self.max_passed = -1
        
        elif mode == 'test':
            success = self._old_checks(candidate)
            self._record_call(updates, mode, start_s, success)
            return success
        
        elif mode == 'optional':
            if not self._old_checks(candidate):
                self._record_call(updates, mode, start_s, False)
                return False
        
        else:
            raise ValueError(f'Unsupported update mode: {mode}')
        
        passed_checks = []
        failed_checks = []
        for check_idx, check in enumerate(self.checks, 1):
            label = check['label']
            progress = f'({check_idx}/{self.nr_checks})'
            self.logger.info(f'Check {progress}: {label}.')
            if self._check(candidate, check):
                passed_checks += [check]
            else:
                failed_checks += [check]
                break

        nr_passed = len(passed_checks)
        self.logger.info(f'Candidate passes {nr_passed} checks.')
        if nr_passed > self.max_passed:
            self.logger.info(f'Updating composition (mode: {mode}).')
            self.max_passed = nr_passed
            self.composition = candidate
            self.passed_checks = passed_checks
            self.failed_checks = failed_checks
            self._record_call(updates, mode, start_s, True)
            return True
        else:
            self.logger.info(f'Do not update composition (force: {mode}).')
            self._record_call(updates, mode, start_s, False)
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
            cache_key = self._get_key(composition, check)
            cache = check['cache']
            result = cache.get(cache_key)
            self.logger.info(f'Retrieved check result from cache: {result}')
            return result
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
            min_comp = self._expand_composition(min_comp, composition)
            check['last_used_ids'] = min_comp.keys()
            
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
            code = self.ops.get_ops(task_id)[code_id]
            parts += [code]
        return '\n\n'.join(parts)
    
    def _expand_composition(self, min_comp, full_comp):
        """ Update list of dependencies in task using code. 
        
        Args:
            min_comp: composition with code for required tasks
            full_comp: composition integrating all prior tasks
        
        Returns:
            composition expanded by required tasks
        """
        changed = True
        while changed:
            changed = False
            expanded_comp = min_comp.copy()
            for task_id, code_id in min_comp.items():
                code = self.ops.get_ops(task_id)[code_id]
                used_ids = self._used_task_ids(code)
                for used_id in used_ids:
                    if used_id not in min_comp:
                        used_code_id = full_comp[used_id]
                        expanded_comp[used_id] = used_code_id
                        changed = True
                
            min_comp = expanded_comp

        return min_comp
    
    def _used_task_ids(self, code):
        """ Returns IDs of tasks whose functions are called.
        
        Args:
            code: analyze this piece of code
        
        Returns:
            set of task IDs
        """
        task_ids = set()
        for fct_name, task_id in self.fct2tid.items():
            def_pattern = f'def {fct_name}('
            pattern = f'{fct_name}('
            if pattern in code and not def_pattern in code:
                task_ids.add(task_id)
        
        return task_ids
    
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
        
        sub_comp = self._expand_composition(sub_comp, composition)
        return frozenset(sub_comp.items())
    
    def _old_checks(self, candidate):
        """ Re-perform checks for candidate composition passed by others.
        
        Args:
            candidate: check this candidate composition.
            
        Returns:
            True iff candidate passes more checks than prior compositions.
        """
        old_checks = self.passed_checks + self.failed_checks
        old_checks.sort(key=lambda c:self._selectivity(c))
        nr_checks = len(old_checks)
        
        for idx, old_check in enumerate(old_checks, 1):
            label = old_check['label']
            selectivity = self._selectivity(old_check)
            self.logger.info(
                f'Trying old check {idx}/{nr_checks}: ' +\
                f'{label} (selectivity: {selectivity})')
            progress = f'{self.max_passed}/{self.nr_checks}'
            self.logger.info(f'Best composition passes {progress} checks.')
            if not self._check(candidate, old_check):
                return False
        
        return True
    
    def _record_call(self, updates, mode, start_s, success):
        """ Add entry describing update to call history.
        
        Args:
            updates: maps updated tasks to new code IDs
            mode: update mode ("force", "optional", "test")
            start_s: start time of call
            success: whether update was successful
        """
        total_s = time.time() - start_s
        self.history += [{
            "updates":updates,
            "mode":mode,
            "start_s":start_s,
            "total_s":total_s,
            "success":success
            }]
    
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
        
        self.logger.info(f'Scheduled Checks:')
        for task_idx in range(self.nr_tasks):
            task_id = self.task_order[task_idx]
            self.logger.info(f'Task {task_idx} ({task_id}) Checks:')
            checks = idx2checks[task_idx]
            for check in checks:
                check_type = check['type']
                assert check_type in ['sql', 'code']
                if check_type == 'sql':
                    query = check['query']
                    self.logger.info(f'SQL: {query}')
                else:
                    filename = check['file']
                    self.logger.info(f'Code: {filename}')
                requirements = check['requirements']
                self.logger.info(f'  Requires {requirements}')
        
        return idx2checks
    
    def _selectivity(self, check):
        """ Calculates selectivity of check using cache content.
        
        Args:
            check: estimate probability to pass this check
        
        Returns:
            a selectivity number between 0 and 1 (default: 0.49999)
        """
        if 'cache' in check:
            comp2result = check['cache']
            nr_checked = len(comp2result)
            nr_passed = sum(comp2result.values())
            return float(nr_passed) / nr_checked
        else:
            return 0.49999