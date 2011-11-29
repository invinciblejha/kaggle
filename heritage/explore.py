from __future__ import division
"""
    Explore Heritage .csv files
"""
import math
import os
import csv

def get_counts_dict(path):
    """Read a Heritage .csv file 
        Top row is column keys. Left column is patient id in all .csv files 
    """
    data_reader = csv.reader(open(path, 'rb'), delimiter=',', quotechar='"')
    column_keys = data_reader.next()
    counts_dict = {}
    for row in data_reader:
        patient_key = row[0]
        patient_vals = row[1:]
        counts_dict[patient_key] = counts_dict.get(patient_key, 0) + 1 
    
    return column_keys, counts_dict

def show_counts(path): 
    _, counts_dict = get_counts_dict(path)
    
    patient_keys = list(counts_dict.keys())
    patient_keys.sort(key = lambda x: (-counts_dict[x], x))
    
    print 'Counts'
    print 'max = %d' % counts_dict[patient_keys[0]]
    print 'min = %d' % counts_dict[patient_keys[-1]]
    print 'mean = %f' % (sum(counts_dict.values())/len(counts_dict))
    
if __name__ == '__main__':
    import sys
    import optparse

    parser = optparse.OptionParser('python ' + sys.argv[0] + ' options <file name>')
    #parser.add_option('-r', '--ratio', dest='ratio', default='1.0', help='resampling ratio')
    (options, args) = parser.parse_args()
    path = args[0]
    
    show_counts(path)
    
    
   
    