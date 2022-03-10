'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import abc
import dbz.code
import dbz.plan
import pandas as pd
import psycopg2
import subprocess


class Engine(abc.ABC):
    """ An engine processes SQL queries. """
    
    @abc.abstractclassmethod
    def execute(self, sql, out):
        """ Executes given query and writes out result. 
        
        Args:
            sql: SQL query
            out: name of output file
        """
        raise NotImplementedError()


class DbzEngine(Engine):
    """ Executes given query plans. """
    
    def __init__(self, paths, library):
        """ Initializes with given paths.
        
        Args:
            paths: relevant paths for DB-zero
            library: library with operator code
        """
        self.paths = paths
        self.library = library
        self.planner = dbz.plan.Planner(paths.tmp_dir, paths.plan_path)
        self.coder = dbz.code.Coder()
    
    def execute(self, sql, out):
        """ Execute given query and write out result.
        
        Args:
            sql: an SQL query to answer
            out: name of file for query result
        """
        plan = self.planner.plan(sql)
        print(f'Plan: {plan}')
        code_parts = []
        code_parts += [self.library]
        code_parts += [self.coder.plan_code(plan)]
        code_parts += [f'last_result.to_csv("{out}")']
        code = '\n'.join(code_parts)
        print(f'Code: {code}')
        self._run(code)
    
    def _run(self, code):
        """ Execute given Python code.
        
        Args:
            code: Python code to execute
        """
        with open(self.paths.code, 'w') as file:
            file.write(code)
        completed = subprocess.run([
            self.paths.python, self.paths.code],
            capture_output=True)
        if completed.returncode > 0:
            print(f'Error: {completed.stderr}')


class PgEngine(Engine):
    """ Executes queries using Postgres. """
    
    def __init__(self, db, user, pwd):
        """ Initializes Postgres database access. """
        self.db = db
        self.user = user
        self.pwd = pwd
        self.connection = psycopg2.connect(db=db, user=user, password=pwd)
    
    def execute(self, sql, out):
        """ Executes query using Postgres.
        
        Args:
            sql: SQL query to execute
            out: write output to this file
        """
        result = pd.read_sql_query(sql, self.connection)
        result.to_csv(out)