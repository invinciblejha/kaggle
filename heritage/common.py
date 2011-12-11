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

def HEADING():
    print  '=' * 80

def SUBHEADING():
    print  '-' * 80

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

def get_dict_all(filename, xform):
    """Return csv file dict with MemberID as keys
       xform is applied to all values
    """
    column_keys, get_data = get_csv(filename)
    
    print 'get_dict_all(filename=%s, column_keys=%s, xform=%s)' % (filename, column_keys, xform)
    data_dict = {}
    for i, (k,row) in enumerate(get_data()):
        out_row = []
        for v in row:
            try:
                x = xform(v)
            except:
                print '+++ "%s" is invalid format in row %d' % (v,i)
                x = 0    
            out_row.append(x)        
        data_dict[k] = out_row
    print '  num rows = %d' % i    
    return column_keys, data_dict
    
    