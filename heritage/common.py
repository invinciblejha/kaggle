from __future__ import division
"""
    Explore Heritage .csv files
    
    Claims.csv 2,668,990 rows
"""
import math
import os
import random
import re
import csv
import time
import pickle

AGE_LOW = 1
AGE_MEDIUM = 2
AGE_HIGH = 3
AGES = [AGE_LOW, AGE_MEDIUM, AGE_HIGH]

def HEADING():
    print  '=' * 80

def SUBHEADING():
    print  '-' * 80
    
def mk_dir(dir):
    try:
        os.mkdir(dir)
    except:
        pass    

def summarize(title, a_list):
    """Print some summary statistics about a_list"""
    x = sorted(a_list)
    SUBHEADING()
    print 'Summary "%s":' % title
    print 'len = %d' % len(x)
    print 'min = %d' % x[0]
    print 'max = %d' % x[-1]
    print 'mean = %f' % (sum(x)/len(x))
    print 'median = %d' % x[len(x)//2]
    print 'total = %f' % sum(x)

def get_csv(path):
    """Read Heritage csv file
        Returns:
            column_keys: list of column header keys
            get_data(): generator to read rows
    """
    data_reader = csv.reader(open(path , 'rb'), delimiter=',', quotechar='"')
    column_keys = data_reader.next()
    
    def get_data():
        for row in data_reader:
            patient_key = int(row[0])
            data = row[1:]
            yield(patient_key, data)

    return column_keys, get_data

def get_member_ids(filename):
    """Return list of MemberIDs in a Heritage csv file  """
    column_keys, get_data = get_csv(filename)
    
    print 'get_member_ids(filename=%s)' % filename
    assert(column_keys[0] == 'MemberID')

    #return [k for k,_ in get_data()] 
    
    member_ids = []
    for i, (k,_) in enumerate(get_data()):
        member_ids.append(k)
    print '  num rows = %d' % i 
    return member_ids
    
def get_dict(filename, column_key, xform):
    """Return column with header <column_key> as a dict with MemberID as keys
       xform is applied to all values
    """
    column_keys, get_data = get_csv(filename)
    
    print 'filename=%s, key=%s, column_keys=%s, xform=%s' % (filename, column_key, column_keys, xform)
    assert(column_key in column_keys[1:])
    column = column_keys[1:].index(column_key)
    data_dict = {}
    for k,v in get_data():
        try:
            x = xform(v[column])
        except:
            print '+++ "%s" is invalid format in row %d' % (v[column],i)
            x = None    
        if x is not None:
            data_dict[k] = x
    return data_dict


_regex_int = re.compile(r'(\d+)')
def get_int_part(s):
    return int(_regex_int.search(s).group(1))
    
_sex_dict = {'M':0, 'F':1}    
def get_sex(s):
    return _sex_dict[s[0]]

DEFAULT_MAP_FUNCTION = int    
MAP_FUNCTIONS = {
    'DrugCount.csv' : { 
        'Year' : lambda x: int(x[1]), 
        'DSFS' : get_int_part,  
        'DrugCount' : get_int_part  
    },
    'LabCount.csv' : { 
        'Year' : lambda x: int(x[1]), 
        'DSFS' : get_int_part,  
        'LabCount' : get_int_part  
    },
    'Members.csv' : { 
        'AgeAtFirstClaim' : get_int_part, 
        'Sex' : get_sex    
    }
}

def get_map_function(filename, column):
    """Return map function for filename:column"""
    if not filename in MAP_FUNCTIONS.keys():
        return DEFAULT_MAP_FUNCTION
    if not column in MAP_FUNCTIONS[filename].keys():
        return DEFAULT_MAP_FUNCTION
    return MAP_FUNCTIONS[filename][column]    
    
def get_dict_all(filename, xform, verbose = False):
    """Return csv file dict with MemberID as keys
       xform is applied to all values
    """
    column_keys, get_data = get_csv(filename)
    #print 'column_keys', column_keys
    
    if xform:
        col_xforms = [xform for i in range(len(column_keys))]
    else:    
        col_xforms = [get_map_function(filename, column) for column in column_keys[1:]]
        print col_xforms
     
    #print 'get_dict_all(filename=%s, column_keys=%s, xform=%s)' % (filename, column_keys, xform)
    data_dict = {}
    for i, (k,row) in enumerate(get_data()):
        out_row = []
        try:
            for j,v in enumerate(row):
               x = col_xforms[j](v) #xform(v)
               out_row.append(x)  
        except:
            if verbose:
                print '+++ "%s" is invalid format for %s in row %d, col %d' % (v, 
                    column_keys[j+1], i, j), row
            continue       
        data_dict[k] = out_row
    #print '  num rows = %d' % i    
    return column_keys, data_dict
    
def combine_dicts(columns1, dict1, columns2, dict2, use_dict1 = False):
    """Return all columns of dict1 and dict2 that have 
       MemberID as keys
    """    
    combined_columns = columns1 + columns2
    if use_dict1:
        dict2_default = [0 for v in columns2]
        keys = dict1.keys()
        combined_dict = {}
        for k in keys:
            combined_dict[k] = dict1[k] + dict2.get(k, dict2_default)
    else:    
        keys = set(dict1.keys()) & set(dict2.keys())
        combined_dict = {}
        for k in keys:
            combined_dict[k] = dict1[k] + dict2[k]
    
    return combined_columns, combined_dict    
    
    