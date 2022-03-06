'''
Created on Mar 6, 2022

@author: immanueltrummer
'''
class Planner():
    """ Generates JSON plan using Apache Calcite. """
    
    def __init__(self, jar_path):
        """ Initialize with given path to Calcite planner.
        
        Args:
            jar_path: path to .jar file from Apache Calcite.
        """
        self.jar_path = jar_path
    
    def plan(self, sql):
        """ Invoke Calcite planner and generate plan.
        
        Args:
            sql: generate plan for this SQL query
        
        Returns:
            query plan in JSON representation
        """
        # TODO
        return []