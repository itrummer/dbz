from abc import ABC, abstractmethod


class AbstractTable(ABC):
    """ Represents a relational table with data. """
    
    @abstractmethod
    def from_csv(self, csv_path):
        """ Loads table data from csv file. """
        raise NotImplementedError()
    
    @abstractmethod
    def to_csv(self, csv_path):
        """ Writes table data to csv file. """
        raise NotImplementedError()
    
    @abstractmethod
    def add_column(self, column):
        """ Adds given column to table. """
    
    @abstractmethod
    def get_column(self, column_idx):
        """ Returns column with given index. """
        raise NotImplementedError()


class Table(AbstractTable):
    """ <DataInstructions> """
    
    def __init__(self):