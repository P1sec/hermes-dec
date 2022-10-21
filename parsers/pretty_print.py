#!/usr/bin/python3
#-*- encoding: Utf-8 -*-

from collections import OrderedDict


"""
    Turn a parsed C structure in a dict of human-readable key-value
    pairs, for displayal in ASCII tables
    
    :param ctypes_structure: A parsed ctypes structures to consume.
    
    :returns An OrderedDict of strings/strings.
"""

def structure_to_key_values_strings(ctypes_structure):
    
    key_values = OrderedDict()
    
    if not getattr(ctypes_structure, '_fields_', None):
        return key_values
    
    for key, ctype in (field[:2] for field in ctypes_structure._fields_):
        
        value = getattr(ctypes_structure, key)
        
        # Turn "key_name" into "Key name"
        
        pretty_key = key[0].upper() + key[1:]
        pretty_key = pretty_key.replace('_', ' ')
        
        # Stringify the value
        
        if type(value) == bytes: # Strings
            
            key_values[pretty_key] = value.decode('ascii')
        
        elif type(value) == int: # Integer
            
            # key_values[pretty_key] = '0x%08x' % value if value else 'N/A'
            key_values[pretty_key] = str(value) if value < (1 << 15) else hex(value)
        
        else:
            
            key_values[pretty_key] = bytes(value).hex()
    
    return key_values


"""
    Return an ASCII table from a parsed C structure, with field names as
    column 1 and values as column 2.
"""

def pretty_print_structure(ctypes_structure):
    
    key_values = structure_to_key_values_strings(ctypes_structure)
    
    pretty_print_table(list(key_values.items()))


"""
    Return an ascii table from a list (rows) of list (columns) of strings (cells)
"""

def pretty_print_table(rows):
    
    # Calculate columns length
    
    if not rows:
        return
    
    number_of_columns = len(rows[0])
    
    column_to_max_length = [

        max(len(row[column]) for row in rows)
        
        for column in range(number_of_columns)
    ]
    
    # Do a nice table
    
    print()
    
    print('+-%s-+' % '---'.join('-' * max_len for max_len in column_to_max_length))
    
    for row in rows:
        
        print('| %s |' % ' | '.join(
        
            row[column].ljust(column_to_max_length[column])
            
            for column in range(number_of_columns))
        )
        
        print('+-%s-+' % '---'.join('-' * max_len for max_len in column_to_max_length))
        


