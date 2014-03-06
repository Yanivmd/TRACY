from mongokit import Document
import bson

class Function(Document):
    '''
    Represents the entire data DB. 
    Contains groups of subgraphs with high rate of similarity.
    '''
    __database__ = 'function'
    __collection__ = 'functions'
    
    structure = {
        'source_website': basestring,
        'package': basestring,
        'download_link': basestring,
        'elf_name': basestring, 
        'function_name': basestring,
        'subgraphs': [bson.binary.Binary]                      
    }
    
    required_fields = ['elf_name', 'subgraphs']
        