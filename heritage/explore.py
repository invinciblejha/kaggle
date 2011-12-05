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
    print  '-' * 80
    print 'Summary "%s":' % title
    #print 'type = %s' % type(x)
    print 'len = %d' % len(x)
    print 'min = %d' % x[0]
    print 'max = %d' % x[-1]
    print 'mean = %f' % (sum(x)/len(x))
    print 'median = %d' % x[len(x)//2]

def get_csv(path):
    data_reader = csv.reader(open(path , 'rb'), delimiter=',', quotechar='"')
    column_keys = data_reader.next()
    
    def get_data():
        for row in data_reader:
            patient_key = row[0]
            data = row[1:]
            yield(patient_key, data)
            
    return column_keys, get_data
    
def get_dict(filename, key, xform):
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

def get_annotated_data(filename, key, xform):
    column_keys, data_dict = get_dict(filename, key, xform)
    return {'filename':filename, 'column':key, 'data':data_dict}
    
def get_counts(filename, key):
    """Return counts for all values of key in filename"""
    column_keys, get_data = get_csv(filename)
    assert(key in column_keys[1:])
    column = column_keys[1:].index(key)
    print 'getcounts() %s : %s column = %d' % (filename, key, column+1) 
    counts_dict = {}
    for i,(k,v) in enumerate(get_data()):
        x = v[column]
        counts_dict[x] = counts_dict.get(x, 0) + 1
    return counts_dict  
    
def get_all_counts(filename):
    """Return counts for all values of all keys in filename"""
    column_keys, get_data = get_csv(filename)
    all_counts_dict = {}
    for key in column_keys[1:]:
        all_counts_dict[key] = {}

    for i,(k,v) in enumerate(get_data()):
        for key in column_keys[1:]:
            column = column_keys[1:].index(key)
            x = v[column]
            all_counts_dict[key][x] = all_counts_dict[key].get(x, 0) + 1
    return all_counts_dict    

def show_counts_dict(counts_dict):
    if len(counts_dict) <= 50:
        for i,k in enumerate(sorted(counts_dict.keys(), key = lambda x: -counts_dict[x])):
            print '%2d: %25s %7d' % (i, k, counts_dict[k])
    total = sum(counts_dict.values())        
    print '%s : %s has %d unique entries in %d total entries. Average %.1f' % (table, column, 
        len(counts_dict), total, total/len(counts_dict)) 
            
def get_counts_by_patient(filename, key):
    column_keys, get_data = get_csv(filename)
    assert(key in column_keys[1:])
    column = column_keys[1:].index(key)
    print 'get_counts_by_patient() %s : %s column = %d' % (filename, key, column+1) 
    patient_counts_dict = {}
    for i,(patient_key,row) in enumerate(get_data()):
        patient_counts_dict[patient_key] = patient_counts_dict.get(patient_key, {})
        counts_dict = patient_counts_dict[patient_key]
        x = row[column]
        counts_dict[x] = counts_dict.get(x, 0) + 1
    return patient_counts_dict 
    
def show_patient_counts(description, patient_counts_dict):
    if True:
        patient_counts = [len(v) for v in patient_counts_dict.values()]
        summarize('patient counts for %s' % description, patient_counts)

        max_patient_len = 0
        for k,v in patient_counts_dict.items():
            if len(v) >= max_patient_len:
                max_patient_key = k
                max_patient_len = len(v)

        SUBHEADING()        
        print 'Max patient (count) = %s' % max_patient_key
        max_patient_val = patient_counts_dict[max_patient_key]
        for k in sorted(max_patient_val.keys(), key = lambda x: -max_patient_val[x]):
            print '%12s:%4d' % (k, max_patient_val[k])

    patient_totals = [sum(v.values()) for v in patient_counts_dict.values()]
    summarize('patient totals for %s' % description, patient_totals)
        
    max_patient_total = 0
    for k,v in patient_counts_dict.items():
        if sum(v.values()) >= max_patient_total:
            max_patient_key = k
            max_patient_total = sum(v.values()) 
            
    SUBHEADING()        
    print 'Max patient (total) = %s' % max_patient_key
    max_patient_val = patient_counts_dict[max_patient_key]
    for k in sorted(max_patient_val.keys(), key = lambda x: -max_patient_val[x]):
        print '%12s:%4d' % (k, max_patient_val[k])    
            
if False: 
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
    d = math.sqrt(float(dx**2 + dy**2))
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
    
def plot_scatter(annotated_data_x, annotated_data_y1, annotated_data_y2 = None):
    import matplotlib.pyplot as plt
    
    data_x = annotated_data_x['data']
    data_y = [annotated_data_y1['data']]
    
    label_x = '%s : %s'% (annotated_data_x['filename'], annotated_data_x['column'])
    label_y = ['%s :% s'% (annotated_data_y1['filename'], annotated_data_y1['column'])]
       
    if annotated_data_y2:
       data_y.append(annotated_data_y2['data'])
       label_y .append('%s :% s'% (annotated_data_y2['filename'], annotated_data_y2['column']))
       
    summarize(label_x, data_x.values())
    for j in range(len(data_y)):
        summarize(label_y[j], data_y[j].values())
   
    def plot_one(data_x,data_y, color, interval):
      
        # Reduce data to largest common subset
        keys = sorted(set(data_x.keys()) & set(data_y.keys()))
        keys = keys[int(len(keys)*interval[0]):int(len(keys)*interval[1])] 
        x = [data_x[k] for k in keys]
        y = [data_y[k] for k in keys] 
        
        # Add some jitter
        x,y = jitter(x,y)
        plt.scatter(x, y, s=1, lw = 0, color=color)
    
    colors = ['blue', 'red']
    for i in range(10):
        interval = (i/10,(i+1)/10)
        for j in range(len(data_y)):
            k = (j+i) % len(data_y)
            plot_one(data_x, data_y[k], colors[k], interval)
                
    plt.xlabel(label_x)
    plt.ylabel(' - '.join(label_y))            
    plt.show()

def plot_histo(annotated_data_x, annotated_data_y1, annotated_data_y2 = None):
    import matplotlib.pyplot as plt
    import graphing
    
    data_x = annotated_data_x['data']
    data_y = [annotated_data_y1['data']]
    
    label_x = '%s : %s'% (annotated_data_x['filename'], annotated_data_x['column'])
    label_y = ['%s :% s'% (annotated_data_y1['filename'], annotated_data_y1['column'])]
       
    if annotated_data_y2:
       data_y.append(annotated_data_y2['data'])
       label_y .append('%s :% s'% (annotated_data_y2['filename'], annotated_data_y2['column']))
       
    summarize(label_x, data_x.values())
    for j in range(len(data_y)):
        summarize(label_y[j], data_y[j].values())
   
    def plot_one(data_x, data_y, color, label_x, label_y):
      
        print 'plot_one', len(data_x), len(data_y), color
        # Reduce data to largest common subset
        keys = sorted(set(data_x.keys()) & set(data_y.keys()))
        x = [data_x[k] for k in keys]
        y = [data_y[k] for k in keys] 
        counts = {}
        for k in keys:
            ix = data_x[k]
            if not ix in counts.keys():
                counts[ix] = {}
            iy = data_y[k]
            if not iy in counts[ix].keys():
                counts[ix][iy] = 0
            counts[ix][iy] += 1
        
        print 'graphing.plot_2d_histo', len(counts), color    
        graphing.plot_2d_histo(counts, color, label_x, label_y)        
        
            
    colors = ['blue', 'red']
    for j in range(len(data_y)):
        plt.subplot(len(data_y), 1, j+1)
        plot_one(data_x, data_y[j], colors[j], label_x, label_y[j])
   
    plt.show()
    
TABLES_IN = [
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

TABLES_CLAIMS = [
    'Claims.csv',
    #  Claims_20.csv'
    # Claims_200.csv'
]

TABLES_DERIVED = [
    'derived_Claims.csv'
    # NumClaims is an effect
]

TABLES_OUT = [
    'DaysInHospital_Y2.csv',
    'DaysInHospital_Y3.csv',
]

TABLES = TABLES_IN + TABLES_CLAIMS + TABLES_OUT

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

def get_map_function(table, column):
    if not table in MAP_FUNCTIONS.keys():
        return DEFAULT_MAP_FUNCTION
    if not column in MAP_FUNCTIONS[table].keys():
        return DEFAULT_MAP_FUNCTION
    return MAP_FUNCTIONS[table][column]
    

def get_main_pcg_dict(filename):
    column_keys, get_data = get_csv(filename)

    pcg_column = column_keys[1:].index('PrimaryConditionGroup')
    pcg_counts_dict = {}
    pcg_keys = set([])
    for k,v in get_data():
        pcg = v[pcg_column]
        pcg_keys.add(pcg)
        pcg_counts_dict[k] = pcg_counts_dict.get(k, {})
        pcg_counts_dict[k][pcg] = pcg_counts_dict[k].get(pcg, 0) + 1
    
    main_pcg_dict = {}
    for patient_key, patient_pcgs in pcg_counts_dict.items():
        highest_pcg_count = 0
        for pcg in patient_pcgs.keys():
            if patient_pcgs[pcg] >= highest_pcg_count:
                main_pcg = pcg
        main_pcg_dict[patient_key] = main_pcg
        
    return main_pcg_dict, pcg_keys    

def get_max_key(a_dict):
    max_val = 0
    for k,v in a_dict.items():
        if v >= max_val:
            max_key = k
            max_val = v
    return max_key
    
PCG_LIST = [  
    
     'MISCL1',
     'MISCL5',
     'PRGNCY',
     'ROAMI',
     'RESPR4',
     'FXDISLC',
     'METAB3',
     'GYNEC1',
     'METAB1',
     'NEUMENT',
     'APPCHOL',
     'ARTHSPIN',
     'MSC2a3',
     'TRAUMA',
     'RENAL3',
     'CANCRB',
     'CANCRM',
     'RENAL2',
     'PERVALV',
     'AMI',
     'COPD',
     'GIOBSENT',
     'HEMTOL',
     'UTI',
     'CHF',
     'GYNECA',
     'STROKE',
     'HEART2',
     'GIBLEED',
     'HEART4',
     'LIVERDZ',
     'CATAST',
     'INFEC4',
     'PNEUM',
     'ODaBNCA',
     'MISCHRT',
     'SKNAUT',
     'SEPSIS',
     'HIPFX',
     'SEIZURE',
     'CANCRA',
     'FLaELEC',
     'PNCRDZ',
     'RENAL1',
     'PERINTL',
]

PCG_LUT = {}
for i,pcg in enumerate(sorted(PCG_LIST)):
    PCG_LUT[pcg] = i + 1

def get_pcg_index(pcg):
    if pcg in PCG_LUT.keys():
        return PCG_LUT[pcg]
    if pcg:
        print "     '%s'" % pcg
        exit()
    return 0

def make_group_name(group):
    return os.path.join('CACHE', 'group%04d.pkl' % group)
    
DERIVED_PREFIX = 'derived_'
DERIVED_COLUMN_KEYS = ['MemberID', 'NumClaims', 'PrimaryConditionGroup'] 
     
def make_derived_table(filename):
    column_keys, get_data = get_csv(filename)

    year_column = column_keys[1:].index('Year')
    pcg_column = column_keys[1:].index('PrimaryConditionGroup')
   
    #pcg_keys = list(PCG_LUT.keys())
    
    t0 = time.clock()
    
    NUM_GROUPS = 100
    num_rows = 0
    for group in range(NUM_GROUPS):
        derived_dict = {'ALL':{}, 'Y1':{}, 'Y2':{}, 'Y3':{}}
        print 'group=%d' % group
        _, get_data = get_csv(filename)
        for k,v in get_data():
            if (int(k) % NUM_GROUPS) != group:
                continue
            year = v[year_column]
            pcg = get_pcg_index(v[pcg_column])
            #if not v[pcg_column] in pcg_keys:
            #   pcg_keys.append(v[pcg_column])
                #print '>', v[pcg_column]
            #print '"%s" => %d' % (v[pcg_column], pcg)
            
            if num_rows and num_rows % 10000 == 0:
                t = time.clock() - t0
                eta  = int(t * (2668990 - num_rows)/num_rows)
                print ' %8d row (%4.1f%%) %7.1f sec, %4d rows/sec, eta = %6d sec' % (num_rows, 
                    100.0 * num_rows/2668990, t, int(num_rows/t), eta) 

            for y in (year, 'ALL'):
                if not k in derived_dict[y].keys():
                    derived_dict[y][k] = [0, {}] 
                derived_dict[y][k][0] += 1
                derived_dict[y][k][1][pcg] = derived_dict[y][k][1].get(pcg, 0) + 1 
                
            num_rows += 1
        
        print 'Coallescing'       
        for year in derived_dict:
            for k in derived_dict[year].keys():
                if int(k) % NUM_GROUPS != group:
                    continue
                derived_dict[year][k][1] = get_max_key(derived_dict[year][k][1]) 
        pickled_path = make_group_name(group)            
        pkl_file = open(pickled_path , 'wb')
        pickle.dump(derived_dict, pkl_file, -1)   # Pickle the data using the highest protocol available.
        pkl_file.close()  

    derived_dict = {'ALL':{}, 'Y1':{}, 'Y2':{}, 'Y3':{}}    
    for group in range(NUM_GROUPS):
        pickled_path = make_group_name(group)            
        pkl_file = open(pickled_path , 'rb')
        part_dict = pickle.load(pkl_file)   
        pkl_file.close()
        for y,d in part_dict.items():
            for k,v in d.items():
                derived_dict[y][k] = (part_dict[y][k][0], part_dict[y][k][1]) 

    if False:
        print '-' *80
        for k in pcg_keys:
            print "     '%s'," % k            
        exit()  
    
    for year in derived_dict:
        derived_filename = '%s%s_%s' % (DERIVED_PREFIX, year, filename)
        data_writer = csv.writer(open(derived_filename , 'wb'), delimiter=',', quotechar='"')
        data_writer.writerow(DERIVED_COLUMN_KEYS)
        for k in sorted(derived_dict[year].keys()):
            v = derived_dict[year][k]
            #print ' ', derived_dict[year][k], v2
            data_writer.writerow([k, str(v[0]), str(v[1])])

if __name__ == '__main__':
    import sys
    import optparse

    parser = optparse.OptionParser('python ' + sys.argv[0] + ' options <file name>')
    parser.add_option('-x', '--x-table-column', dest='x_table_column', default='', help='x table:column')
    parser.add_option('-y', '--y-table-column',  dest='y_table_column',  default='', help='y table:column')
    parser.add_option('-Y', '--y-table-column-2', dest='y2_table_column', default=None, help='y2 table:column')
    parser.add_option('-a', '--all-outputs-for-y', action="store_true", dest='all_outputs', default=False, help='plot all outputs')
    parser.add_option('-d', '--derive-values', dest='derive_values_from', default='', help='derive values from table')
    parser.add_option('-u', '--counts', dest="counts_table_column", default='', help='show counts for table:column')  
    parser.add_option('-p', '--patient-counts', dest="patient_counts_table_column", default='', help='show patient counts for table:column')  
    parser.add_option('-t', '--tables', action="store_true", dest='show_tables', default=False, help='show the base tables')
    parser.add_option('-c', '--columns', action="store_true", dest='show_columns', default=False, help='show columns in the base tables')
  
    (options, args) =  parser.parse_args()
    
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

    if options.counts_table_column: 
        if not ':' in options.counts_table_column:
            table = options.counts_table_column
            all_counts_dict = get_all_counts(table)
            for column in sorted(all_counts_dict.keys(), key = lambda x: len(all_counts_dict[x])):
                SUBHEADING()
                print column
                show_counts_dict(all_counts_dict[column])
        else:    
            table, column = options.counts_table_column.split(':')
            counts_dict = get_counts(table, column)
            show_counts_dict(counts_dict)
        exit()
        
    if options.patient_counts_table_column:
        table, column = options.patient_counts_table_column.split(':')
        patient_counts_dict = get_counts_by_patient(table, column)   
        show_patient_counts('%s : %s' % (table, column), patient_counts_dict)
        
    if options.derive_values_from:
        make_derived_table(options.derive_values_from)
    
    y_table_column = y2_table_column = None
    if options.all_outputs:
        y_table_column = 'DaysInHospital_Y2.csv:DaysInHospital'
        y2_table_column = 'DaysInHospital_Y3.csv:DaysInHospital'
    if options.y_table_column:
        y_table_column = options.y_table_column
    if options.y2_table_column:
        y2_table_column = options.y2_table_column
        
    if y_table_column:
        y_table, y_column = y_table_column.split(':')
        y_data = get_annotated_data(y_table, y_column, get_map_function(y_table, y_column))
        
        if y2_table_column:
            y2_table, y2_column = y2_table_column.split(':')
            y2_data = get_annotated_data(y2_table, y2_column, get_map_function(y2_table, y2_column))

        if options.x_table_column:
            x_table, x_column = options.x_table_column.split(':')
            SUBHEADING()
            print x_column
            x_data = get_annotated_data(x_table, x_column, get_map_function(x_table, x_column))
            plot_histo(x_data, y_data, y2_data)
        else:
            for x_table in TABLES_IN + TABLES_DERIVED:
                #if x_table in ['DrugCount.csv', 'LabCount.csv']:
                #    continue
                HEADING()
                print x_table    
                column_keys, _ = get_csv(x_table)
                for x_column in column_keys[1:]:
                    SUBHEADING()
                    print x_column
                    x_data = get_annotated_data(x_table, x_column, get_map_function(x_table, x_column))
                    plot_histo(x_data, y_data, y2_data)
    
  
    
   
    