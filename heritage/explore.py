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

def summarize(title, a_list):
    """Print some summary statistics about a_list"""
    x = sorted(a_list)
    print 'Summary %s:' % title
    print 'min = %d' % x[0]
    print 'max = %d' % x[-1]
    print 'mean = %f' % (sum(x)/len(x))
    print 'median = %d' % x[len(x)//2]
    print  '-' * 40

def show_counts(counts_dict): 
    
    patient_keys = list(counts_dict.keys())
    patient_keys.sort(key = lambda x: (-counts_dict[x], x))
    
    print 'Counts'
    print 'max = %d' % counts_dict[patient_keys[0]]
    print 'min = %d' % counts_dict[patient_keys[-1]]
    print 'mean = %f' % (sum(counts_dict.values())/len(counts_dict))

OUTCOMES_FILE = 'DaysInHospital_Y2.csv'    
def get_outcomes_dict():
    data_reader = csv.reader(open(OUTCOMES_FILE , 'rb'), delimiter=',', quotechar='"')
    column_keys = data_reader.next()
    outcome_dict = {}
    for row in data_reader:
        patient_key = row[0]
        outcome = int(row[2])
        outcome_dict[patient_key] = outcome 
    
    return column_keys, outcome_dict
    
def plot_outcomes_vs_counts(counts_dict, outcomes_dict):
    import matplotlib.pyplot as plt
    #from pylab import xlabel, ylabel
    
    y = outcomes_dict.values()
    x = [counts_dict.get(k, -1) for k in outcomes_dict.keys()]
    
    summarize('counts', x)
    summarize('days in hospital', y)
    plt.scatter(x, y)
    plt.xlabel('counts')
    plt.ylabel('days in hospital')
    plt.show()
    
if __name__ == '__main__':
    import sys
    import optparse

    parser = optparse.OptionParser('python ' + sys.argv[0] + ' options <file name>')
    #parser.add_option('-r', '--ratio', dest='ratio', default='1.0', help='resampling ratio')
    (options, args) = parser.parse_args()
    path = args[0]
    
    _, counts_dict = get_counts_dict(path)
    _, outcomes_dict = get_outcomes_dict()
    
    #show_counts(path)
    plot_outcomes_vs_counts(counts_dict, outcomes_dict)
    
   
    