'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import abc
import dbz.execute.code
import dbz.execute.query
import dbz.execute.plan
import logging
import pandas as pd
import psycopg2
import subprocess
import time


class Engine(abc.ABC):
    """ An engine processes SQL queries. """
    
    def __init__(self, collect_stats):
        """ Initialize engine.
        
        Args:
            collect_stats: whether to collect execution statistics
        """
        self.collect_stats = collect_stats
        self.stats = []
    
    @abc.abstractclassmethod
    def execute(self, sql, out):
        """ Executes given query and writes out result. 
        
        Args:
            sql: SQL query
            out: name of output file
        
        Returns:
            True iff execution succeeds
        """
        raise NotImplementedError()
    
    def print_stats(self):
        """ Print out execution statistics. """
        print('plan_s\ttotal_s\tsuccess')
        for stats in self.stats:
            plan_s = stats['planning_s']
            total_s = stats['total_s']
            success = stats['success']
            print(f'{plan_s}\t{total_s}\t{success}')
    
    def _record_stats(self, query, success, plan_s=-1, total_s=-1):
        """ Records execution statistics if corresponding flag is enabled. 
        
        Args:
            query: this SQL query was executed
            success: whether query execution was successful
            plan_s: seconds spent in query planning
            total_s: total seconds spent in query evaluation
        """
        if self.collect_stats:
            self.stats += [{
                "query":query, "success":success, 
                "planning_s":plan_s, "total_s":total_s
            }]


class DbzEngine(Engine):
    """ Executes given query plans. """
    
    def __init__(self, paths, library, python_path, collect_stats=False):
        """ Initializes with given paths.
        
        Args:
            paths: relevant paths for DB-zero
            library: library with operator code
            python_path: path to Python executable
            collect_stats: whether to collect performance statistics
        """
        super().__init__(collect_stats)
        self.logger = logging.getLogger('all')
        self.paths = paths
        self.library = library
        self.python_path = python_path
        self.error_lines = []
        """ Contains error string produced in last run. """
        
        self.rewriter = dbz.execute.query.Rewriter(paths.schema)
        self.planner = dbz.execute.plan.Planner(
            paths.schema, paths.planner, paths.tmp_dir)
        self.coder = dbz.execute.code.Coder(paths, True)
    
    def add_context(self, query_code, out_path=None):
        """ Add context to given piece of code.
        
        Args:
            query_code: core code for query processing
            out_path: path for result output
        
        Returns:
            completed code with libraries and output commands
        """
        code_parts = []
        code_parts += [self.library]
        import_path = f'{self.paths.includes}/imports.py'
        fct_path = f'{self.paths.includes}/functions.py'
        code_parts += self._include(import_path)
        code_parts += self._include(fct_path)
        code_parts += [query_code]
        if out_path is not None:
            code_parts += [f'write_to_csv(last_result, "{out_path}")']
        return '\n'.join(code_parts)
        
    def execute(self, sql, out):
        """ Execute given query and write out result.
        
        Args:
            sql: an SQL query to answer
            out: name of file for query result
        
        Returns:
            true iff execution succeeds
        """
        start_s = time.time()
        code = self.sql2code(sql, out)
        plan_s = time.time() - start_s
        success = self.run(code)
        total_s = time.time() - start_s
        self._record_stats(sql, success, plan_s, total_s)
        return success
    
    def run(self, code):
        """ Execute given Python code.
        
        Args:
            code: Python code to execute
        
        Returns:
            True iff execution succeeds
        """
        with open(self.paths.code, 'w') as file:
            file.write(code)
        completed = subprocess.run([
            self.python_path, self.paths.code],
            capture_output=True)
        if completed.returncode > 0:
            error_text = str(completed.stderr)
            print(f'Error: {error_text}')
            self.error_lines = [error_text]
            return False
        else:
            return True
    
    def sql2code(self, sql, out):
        """ Generate Python code for processing SQL query.
        
        Args:
            sql: an SQL query to process
            out: name of query result file
        
        Returns:
            a piece of code processing the query
        """
        sql = self.rewriter.rewrite(sql)
        self.logger.info(f'Simplified query: {sql}')
        plan = self.planner.plan(sql)
        self.logger.debug(f'Plan: {plan}')
        query_code = self.coder.plan_code(plan)
        return self.add_context(query_code, out)
    
    def _include(self, path):
        """ Loads code from file.
        
        Args:
            path: load code from this file
        
        Returns:
            list of code lines
        """
        with open(path) as file:
            return [file.read()]


class PgEngine(Engine):
    """ Executes queries using Postgres. """
    
    def __init__(self, db, user, pwd, host, collect_stats=False):
        """ Initializes Postgres database access. 
        
        Args:
            db: name of Postgres database
            user: name of Postgres user
            pwd: password for Postgres database
            host: Postgres host path
            collect_stats: whether to record execution statistics
        """
        super().__init__(collect_stats)
        self.db = db
        self.user = user
        self.pwd = pwd
        self.host = host
    
    def execute(self, sql, out):
        """ Executes query using Postgres.
        
        Args:
            sql: SQL query to execute
            out: write output to this file
        """
        try:
            with psycopg2.connect(
                database=self.db, user=self.user, 
                password=self.pwd, host=self.host) as connection:
                start_s = time.time()
                result = pd.read_sql_query(sql, connection)
                result.to_csv(out, index=False, header=None)
                total_s = time.time() - start_s
                self._record_stats(sql, True, total_s=total_s)
                return True
        except Exception as e:
            print(f'Exception while processing SQL query: {e}')
            return False