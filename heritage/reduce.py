from __future__ import division
"""
    Reduce Heritage .csv files
    
    Claims.csv 2,668,990 rows
"""
import math
import os
import re
import time
import csv
import pickle
import common

DATA_DIRECTORY = 'data2'
common.mk_dir(DATA_DIRECTORY)

DERIVED_PREFIX = os.path.join(DATA_DIRECTORY, 'derived_')

    
def make_group_name(group):
    return os.path.join('CACHE', 'group%04d.pkl' % group)    

def process_multi_pass(filename, init_func, update_func, prefix, DERIVED_COLUMN_KEYS, 
    NUM_GROUPS = 100):
    """This has got complicated due to python running slowing with large dicts
        Passes through input file multiple times and writes partial results to 
        disk (see group).
        
        init_func() returns the initial value of derived_list 
        update_func(derived_list, input_row) updates derived_list based on input_row
    """
    column_keys, get_data = common.get_csv(filename)

    year_column = column_keys[1:].index('Year')
    pcg_column = column_keys[1:].index('PrimaryConditionGroup')
       
    t0 = time.clock()
    num_rows = 0
    
    for group in range(NUM_GROUPS):
        derived_dict = {'ALL':{}, 'Y1':{}, 'Y2':{}, 'Y3':{}}
        print 'group=%d' % group
        _, get_data = common.get_csv(filename)
        for k,v in get_data():
            if (int(k) % NUM_GROUPS) != group:
                continue
            year = v[year_column]
            pcg = get_pcg_index(v[pcg_column])
                        
            if num_rows and num_rows % 10000 == 0:
                t = time.clock() - t0
                eta  = int(t * (2668990 - num_rows)/num_rows)
                print ' %8d row (%4.1f%%) %7.1f sec, %4d rows/sec, eta = %6d sec' % (num_rows, 
                    100.0 * num_rows/2668990, t, int(num_rows/t), eta) 

            for y in (year, 'ALL'):
                if not k in derived_dict[y].keys():
                    derived_dict[y][k] = init_func() 
                update_func(derived_dict[y][k], v)
            num_rows += 1
 
        print 'Saving'        
        pickled_path = make_group_name(group)            
        pkl_file = open(pickled_path , 'wb')
        pickle.dump(derived_dict, pkl_file, -1)   # Pickle the data using the highest protocol available.
        pkl_file.close()  

    print 'Writing to file'
    for year in derived_dict:
        derived_filename = '%s%s_%s_%s' % (DERIVED_PREFIX, prefix, year, filename)
        data_writer = csv.writer(open(derived_filename , 'wb'), delimiter=',', quotechar='"')
        data_writer.writerow(['MemberID'] + DERIVED_COLUMN_KEYS)
        for group in range(NUM_GROUPS):
            pickled_path = make_group_name(group)            
            pkl_file = open(pickled_path , 'rb')
            derived_dict = pickle.load(pkl_file)   
            pkl_file.close()
            for k in sorted(derived_dict[year].keys()):
                row = derived_dict[year][k]
                data_writer.writerow([k] + [str(v) for v in row])

# See pcg.key and Lookup ProcedureGroup.csv   
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
    assert(not pcg)
    return 0 

def make_pcg_counts_table(filename):

    prefix = 'all_counts'
    derived_column_keys = ['None'] + sorted(PCG_LUT.keys(), key = lambda x: PCG_LUT[x])
    
    column_keys, _ = get_csv(filename)
    pcg_column = column_keys[1:].index('PrimaryConditionGroup')

    def init_func():
        return [0 for i in range(len(derived_column_keys))]

    def update_func(derived_list, input_row):
        derived_list[get_pcg_index(input_row[pcg_column])] += 1

    process_multi_pass(filename, init_func, update_func, prefix, derived_column_keys) 
    
def make_lab_counts_table(filename):
    print 'make_lab_counts_table(filename=%s)' % filename
    
    derived_dict = {'Y1':{}, 'Y2':{}, 'Y3':{}}
    column_keys, get_data = common.get_csv(filename)
    year_column = column_keys[1:].index('Year')
    dsfs_column = column_keys[1:].index('DSFS')
    labcount_column = column_keys[1:].index('LabCount')
    print 'year_column=%d' % year_column
    print 'dsfs_column=%d' % dsfs_column
    print 'labcount_column=%d' % labcount_column
    
    dsfs_func = common.get_int_part
    labcount_func = common.get_int_part
    
    for i,(k,v) in enumerate(get_data()):
        year = v[year_column]
        if not k in derived_dict[year].keys():
            derived_dict[year][k] = [0, 0]
        derived_dict[year][k][0] += dsfs_func(v[dsfs_column])
        derived_dict[year][k][1] += labcount_func(v[labcount_column])
        if (i % 10000) == 0: 
            print 'Processed row %d derived_dict = %s' % (i, 
                [(kk,len(vv)) for kk,vv in derived_dict.items()])
        
    print 'Read all rows %d' % i    

    for year in sorted(derived_dict.keys()):
        derived_filename = '%s_%s_%s' % (DERIVED_PREFIX, year, filename)
        data_writer = csv.writer(open(derived_filename , 'wb'), delimiter=',', quotechar='"')
        data_writer.writerow(['MemberID', 'DSFS', 'LabCount'])
        for k in sorted(derived_dict[year].keys()):
            row = derived_dict[year][k]
            data_writer.writerow([k] + [str(v) for v in row])     

if __name__ == '__main__':
    import sys
    import optparse

    parser = optparse.OptionParser('python ' + sys.argv[0] + ' options <file name>')
  
    (options, args) =  parser.parse_args()
    
    if len(args) != 1:
        parser.error("wrong number of arguments")    
    
    filename = args[0]
    
    if 'claims' in filename.lower():
        make_pcg_counts_table(filename)
    elif 'labcount' in filename.lower():
        make_lab_counts_table(filename)    
        