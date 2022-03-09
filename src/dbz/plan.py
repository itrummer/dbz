'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
import json
import subprocess

class Planner():
    """ Generates JSON plan using Apache Calcite. """
    
    def __init__(self, tmp_dir, jar_path):
        """ Initialize with given path to Calcite planner.
        
        Args:
            tmp_dir: use this directory for temporary files
            jar_path: path to .jar file from Apache Calcite.
        """
        self.tmp_dir = tmp_dir
        self.jar_path = jar_path
    
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
            query_file, plan_file],
            capture_output=True)
        if completed.returncode > 0:
            error_msg = completed.stderr
            raise Exception(f'Error: {error_msg}; Query: {sql}')
        with open(plan_file) as file:
            return json.load(file)