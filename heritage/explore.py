from __future__ import division
"""
    Explore Heritage .csv files
"""
import math
import os
import random
import re
import csv

def summarize(title, a_list):
    """Print some summary statistics about a_list"""
    x = sorted(a_list)
    print 'Summary %s:' % title
    #print 'type = %s' % type(x)
    print 'len = %d' % len(x)
    print 'min = %d' % x[0]
    print 'max = %d' % x[-1]
    print 'mean = %f' % (sum(x)/len(x))
    print 'median = %d' % x[len(x)//2]
    print  '-' * 40

def get_csv(path):
    data_reader = csv.reader(open(path , 'rb'), delimiter=',', quotechar='"')
    column_keys = data_reader.next()
    
    def get_data():
        for row in data_reader:
            patient_key = row[0]
            data = row[1:]
            yield(patient_key, data)
            
    return column_keys, get_data
    
def get_dict(filename, key=None, xform=int):
    column_keys, get_data = get_csv(filename)
    if not key:
        return column_keys
    
    print 'filename=%s, key=%s, column_keys=%s, xform=%s' % (filename, key, column_keys, xform)
    assert(key in column_keys[1:])
    column = column_keys[1:].index(key)
    data_dict = {}
    for i,(k,v) in enumerate(get_data()):
        try:
            x = xform(v[column])
        except:
            #print '+++ "%s" is invalid format in row %d' % (v[column],i)
            x = None    
        if x is not None:
            data_dict[k] = x
    return column_keys, data_dict

def get_annotated_data(filename, key, xform=int):
    column_keys, data_dict = get_dict(filename, key, xform)
    return {'filename':filename, 'column':key, 'data':data_dict}
    
def get_annotated_data2(filename_key, xform=int):
    print 'filename_key="%s"' % filename_key
    filename, key = filename_key.split(':')
    return get_annotated_data(filename, key, xform=int)
    
OUTCOMES_FILE = 'DaysInHospital_Y2.csv'   
def get_outcomes_dict():
    column_keys, outcomes_dict = get_dict(OUTCOMES_FILE, 'DaysInHospital')
    print 'outcomes_dict:', len(outcomes_dict)
    return column_keys, outcomes_dict

MEMBERS_FILE = 'Members.csv' 
MEMBERS_AGE_REGEX = re.compile(r'(\d+)[+-]')
def get_member_age(s):
    m = MEMBERS_AGE_REGEX.search(s)
    if not m:
        return None
    return int(m.group(1))
    
def get_members_dict():
    column_keys, members_dict = get_dict(MEMBERS_FILE, 'AgeAtFirstClaim', get_member_age)
    print 'members_dict:', len(members_dict)            
    return column_keys, members_dict
 
def jitter(x, y):
    """Add some 2D radial jitter to points in lists x,y"""  
    dx = max(x) - min(x)
    dy = max(y) - min(y)
    assert(dx > 0)
    assert(dy > 0)
    d = math.sqrt(float(dx^2 + dy^2))
    print 'dx=%d,dy=%d,d=%f' % (dx,dy,d)
    assert(d > 0)
    F = 1.0/15.0
    fx = F*dx/d
    fy = F*dy/d
    
    def j(xx, yy):
        r = random.random() * d
        t = random.random() * 2.0 * math.pi
        return xx+r*math.cos(t)*fx, yy+r*math.sin(t)*fy
    
    xy = [j(x[i],y[i]) for i in range(len(x))]    
    return zip(*xy)
    
def plot_scatter(annotated_data_x, annotated_data_y):
    import matplotlib.pyplot as plt
   
    data_x = annotated_data_x['data']
    data_y = annotated_data_y['data']
    
    label_x = '%s : %s'% (annotated_data_x['filename'], annotated_data_x['column'])
    label_y = '%s :% s'% (annotated_data_y['filename'], annotated_data_y['column'])
    
    summarize(label_x, data_x.values())
    summarize(label_y, data_y.values())
    
    # Reduce data to largest common subset
    keys = set(data_x.keys()) & set(data_y.keys())
    x = [data_x[k] for k in keys]
    y = [data_y[k] for k in keys] 
    
    # Add some jitter
    x,y = jitter(x,y)
    
    plt.scatter(x, y, s=1,  lw = 0)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.show()

TABLES_IN = [
    #'Claims.csv',
    #  Claims_20.csv'
    # Claims_200.csv'
    'DrugCount.csv',
    #   DSFS seems to be an effect
    #   'DrugCount seems to be an effect (more in Y3?)
    'LabCount.csv',
    #   'Year' could be an effect 
    #   DSFS seems to be an effect
    #   LabCount seems to an effect (more in Y3?)
    'Members.csv',
    #   AgeAtFirstClaim seems to a strong effect for Y2 and Y3 
    #   Sex could be an effect "
    #   ClaimsTruncated seems to a strong effect
    #'Target.csv'
]

TABLES_OUT = [
    'DaysInHospital_Y2.csv',
    'DaysInHospital_Y3.csv',
]

TABLES = TABLES_IN + TABLES_OUT

LOOKUPS = [
    'Lookup PrimaryConditionGroup.csv',
    'Lookup ProcedureGroup.csv',
]    

regex_int = re.compile(r'(\d+)')
def get_int_part(s):
    #print '>%s' % s
    #m = regex_int.search(s)
    #print m
    #print m.groups()
    return int(regex_int.search(s).group(1))
    
def get_sex(s):
    if s[0] == 'M':
        return 0
    elif s[0] == 'F':
        return 1
    return None

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

DEFAULT_MAP_FUNCTION = int

def get_map_function(table, column):
    if not table in MAP_FUNCTIONS.keys():
        return DEFAULT_MAP_FUNCTION
    if not column in MAP_FUNCTIONS[table].keys():
        return DEFAULT_MAP_FUNCTION
    return MAP_FUNCTIONS[table][column]        

if __name__ == '__main__':
    import sys
    import optparse

    parser = optparse.OptionParser('python ' + sys.argv[0] + ' options <file name>')
    parser.add_option('-y', '--y-table-column', dest='y_table_column', default='', help='y table:column')
    parser.add_option('-t', '--tables', action="store_true", dest='show_tables', default=False,
                help='show the base tables')
    parser.add_option('-c', '--columns', action="store_true", dest='show_columns', default=False,
                help='show columns in the base tables')            
    (options, args) = parser.parse_args()
    
    if options.show_tables:
        for t in TABLES:
            print t
        exit()
    
    if options.show_columns:
        for t in TABLES:
            print t
            column_keys, _ = get_csv(t)
            for c in column_keys:
                print '    %s' % c
        exit()    
    
    y_data = get_annotated_data2(options.y_table_column)
    for x_table in TABLES_IN:
        #if x_table in ['DrugCount.csv', 'LabCount.csv']:
        #    continue
        print '=' * 80
        print x_table    
        column_keys, _ = get_csv(x_table)
        for x_column in column_keys[1:]:
            print '-' * 80
            print x_column
            map_function = get_map_function(x_table, x_column)
            assert(map_function)
            x_data = get_annotated_data(x_table, x_column, map_function)
            plot_scatter(x_data, y_data)
    
    if False:
        #_, outcomes_dict = get_outcomes_dict()
        #_, members_dict = get_members_dict()
        
        ad_age_at_first_claim = get_annotated_data(MEMBERS_FILE, 'AgeAtFirstClaim', get_member_age)
        ad_days_in_hospital = get_annotated_data(OUTCOMES_FILE, 'DaysInHospital')
        
        #show_counts(path)
        plot_scatter(ad_age_at_first_claim, ad_days_in_hospital)
    
   
    