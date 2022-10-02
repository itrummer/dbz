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
    failed_checks: list
    failed_passes: list
    nr_failed_ops: int
    prior_comps: list
    prior_checks: list


class Composer():
    """ Composes operator implementations into full SQL engine. """
    
    def __init__(self, config, operators, tasks):
        """ Initialize with operator manager. 
        
        Args:
            config: JSON file configuring synthesis
            operators: manages operator implementations
            tasks: manages generation tasks and checks
        """
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
                failed_checks = self.idx2checks[task_idx]
                failed_passes = self.idx2passes[task_idx]
                nr_failed_ops = len(self.ops.get_ids(task_id))
                prior_comps = self.compositions[task_idx-1]
                prior_checks = [
                    c for i in range(task_idx) 
                    for c in self.idx2checks[i]]
                failure_info = FailureInfo(
                    task_id, failed_checks, 
                    failed_passes, nr_failed_ops, 
                    prior_comps, prior_checks)
                logging.info(f'Failure Info ({task_id}): {failure_info}')
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
        
            logging.debug(f'Updating at {task_idx}, next result: {next_result}')
            last_result = self._filter(next_result, task_idx)
            logging.debug(f'Updating at {task_idx}, last result: {last_result}')
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
    
    def _check(self, composition, check):
        """ Apply check to given composition. 
        
        Args:
            composition: maps tasks to selected implementations
            check: a test case for the given composition
        
        Returns:
            True iff the composition passes the check
        """
        library = self._composition_code(composition)
        test_engine = dbz.execute.engine.DbzEngine(
            self.paths, library, self.python)
        
        validator = dbz.execute.check.Validator(
            self.paths, [check], self.sql_ref, self.code_ref)
        return validator.validate(test_engine)
    
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
        
        logging.info(f'Scheduled checks: {idx2checks}')
        return idx2checks