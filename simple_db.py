from mongokit.connection import Connection
from function import Function
import bson

class DBSimpleClient(object):
    '''
    Class for communicating with the database's first version conveniently
    '''
    
    def __init__(self):
        '''
        Sets a connection to mongodb
        '''
        self.connection = Connection()
        self.connection.register([Function]) 
        
    def insert(self, function_data):
        '''
        Inserts given function data to the database
        '''
        function = self.connection.Function()
        function['source_website'] = function_data['source_website']
        function['package'] = function_data['package']
        function['download_link'] = function_data['download_link']
        function['elf_name'] = function_data['elf_name']
        function['function_name'] = function_data['function_name']
        if all(isinstance(s, str) for s in function_data['subgraphs']):
            function['subgraphs'] = [bson.binary.Binary(s) for s in function_data['subgraphs']]
        elif all(isinstance(s, bson.binary.Binary) for s in function_data['subgraphs']):
            function['subgraphs'] = function_data['subgraphs']
        else:
            raise ValueError('Subgraphs type is illegal (not string nor binary)')        
        function.save()

    def get_all(self):
        '''
        Returns the functions data in the DB
        '''
        return [Function(func_doc) for func_doc in self.connection.function.functions.find()[:]]
    
    def connections_number(self):
        return 1