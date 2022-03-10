'''
Created on Mar 10, 2022

@author: immanueltrummer
'''
from abc import ABC, abstractclassmethod

class AbstractTable(ABC):
    """ Represents a relational table with data. """
    
    @abstractclassmethod
    def from_csv(self, csv_path):
        """ Loads table data from csv file. """
        raise NotImplementedError()
    
    @abstractclassmethod
    def to_csv(self, csv_path):
        """ Writes table data to csv file. """
        raise NotImplementedError()
    
    @abstractclassmethod
    def add_column(self, column):
        """ Adds given column to table. """
    
    @abstractclassmethod
    def get_column(self, column_idx):
        """ Returns column with given index. """
        raise NotImplementedError()


class Table(AbstractTable):
    """ <DataInstructions> """