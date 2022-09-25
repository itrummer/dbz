'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import json
import subprocess

class Planner():
    """ Generates JSON plan using Apache Calcite. """
    
    def __init__(self, schema_path, jar_path, tmp_dir):
        """ Initialize with given path to Calcite planner.
        
        Args:
            schema_path: path to database schema file
            jar_path: path to .jar file from Apache Calcite
            tmp_dir: use this directory for temporary files
        """
        self.schema_path = schema_path
        self.jar_path = jar_path
        self.tmp_dir = tmp_dir
    
    def plan(self, sql):
        """ Invoke Calcite planner and generate plan.
        
        Args:
            sql: generate plan for this SQL query
        
        Returns:
            query plan in JSON representation
        """
        query_file = f'{self.tmp_dir}/query.sql'
        plan_file = f'{self.tmp_dir}/plan.json'
        with open(query_file, 'w') as file:
            file.write(sql)
        completed = subprocess.run([
            'java', '-jar', self.jar_path, 
            self.schema_path,
            query_file, plan_file],
            capture_output=True)
        if completed.returncode > 0:
            error_msg = completed.stderr
            raise Exception(f'Error: {error_msg}; Query: {sql}')
        with open(plan_file) as file:
            return json.load(file)