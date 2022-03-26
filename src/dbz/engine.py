'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import abc
import dbz.code
import dbz.query
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
        
        Returns:
            True iff execution succeeds
        """
        raise NotImplementedError()


class DbzEngine(Engine):
    """ Executes given query plans. """
    
    def __init__(self, paths, library, python_path):
        """ Initializes with given paths.
        
        Args:
            paths: relevant paths for DB-zero
            library: library with operator code
            python_path: path to Python executable
        """
        self.paths = paths
        self.library = library
        self.python_path = python_path
        self.planner = dbz.plan.Planner(
            paths.schema, paths.planner, 
            paths.tmp_dir)
        self.coder = dbz.code.Coder(paths)
    
    def execute(self, sql, out):
        """ Execute given query and write out result.
        
        Args:
            sql: an SQL query to answer
            out: name of file for query result
        
        Returns:
            true iff execution succeeds
        """
        sql = dbz.query.simplify(sql)
        print(f'Simplified query: {sql}')
        plan = self.planner.plan(sql)
        print(f'Plan: {plan}')
        code_parts = []
        code_parts += [self.library]
        code_parts += [self.coder.plan_code(plan)]
        code_parts += [f'write_to_csv(last_result, "{out}")']
        code = '\n'.join(code_parts)
        print(f'Code: {code}')
        return self._run(code)
    
    def _run(self, code):
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
            print(f'Error: {completed.stderr}')
            return False
        else:
            return True


class PgEngine(Engine):
    """ Executes queries using Postgres. """
    
    def __init__(self, db, user, pwd, host):
        """ Initializes Postgres database access. 
        
        Args:
            db: name of Postgres database
            user: name of Postgres user
            pwd: password for Postgres database
            host: Postgres host path
        """
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
                result = pd.read_sql_query(sql, connection)
                result.to_csv(out, index=False, header=None)
                return True
        except Exception as e:
            print(f'Exception while processing SQL query: {e}')
            return False