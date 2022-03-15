from abc import ABC, abstractmethod, abstractclassmethod


class Column():
    """ Represents a table column. """
    
    def __init__(self, data):
        self.data = data


class AbstractTable(ABC):
    """ Represents a relational table with data. """
    
    @abstractclassmethod
    def from_csv(cls, csv_path):
        """ Loads table data from csv file (no header). """
        raise NotImplementedError()
    
    @abstractclassmethod
    def from_data(cls, data):
        """ Creates table from in-memory data. """
        raise NotImplementedError()
    
    @abstractmethod
    def to_csv(self, csv_path):
        """ Writes table data to csv file (no header). """
        raise NotImplementedError()
    
    @abstractmethod
    def add_column(self, column):
        """ Adds given column to table. """
        raise NotImplementedError()
    
    @abstractmethod
    def get_column(self, column_idx):
        """ Returns column with given index. """
        raise NotImplementedError()


class Table(AbstractTable):
    """ <DataInstructions> """
    
    def __init__(self):