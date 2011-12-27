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

DATA_DIRECTORY = 'data'
common.mk_dir(DATA_DIRECTORY)

DERIVED_PREFIX = os.path.join(DATA_DIRECTORY, 'derived_')

_serial_number = 0

def update_serial_number():
    global _serial_number
    n = _serial_number
    SERIAL_NUMBER_FILE = os.path.join('CACHE', 'serial.number')
    if os.path.exists(SERIAL_NUMBER_FILE):
        s = file(SERIAL_NUMBER_FILE, 'rt').read()
        print '%s contains "%s"' % (SERIAL_NUMBER_FILE, s)
        n = int(s)
        print 'int=%d' % n
    _serial_number = n + 1
    file(SERIAL_NUMBER_FILE, 'wt').write(str(_serial_number))
    print '_serial_number = %d' % _serial_number

update_serial_number() 

def make_group_name(group):
    return os.path.join('CACHE', 'run%05d_group%04d.pkl' % (_serial_number, group))
    
def get_all_values(filename, column, max_num_values = 100):
    """Return all values of column named columny in file named filename
        
        CharlsonIndex  ['0', '1-2', '3-4', '5+']
        ProcedureGroup ['', 'ANES', 'EM', 'MED', 'PL', 'RAD', 'SAS', 'SCS', 'SDS', 'SEOA', 'SGS', 
                        'SIS', 'SMCD', 'SMS', 'SNS', 'SO', 'SRS', 'SUS']
        Specialty      ['', 'Anesthesiology', 'Diagnostic Imaging', 'Emergency', 'General Practice', 
                        'Internal', 'Laboratory', 'Obstetrics and Gynecology', 'Other', 'Pathology', 
                        'Pediatrics',  'Rehabilitation', 'Surgery']
        PlaceSvc       ['', 'Ambulance', 'Home', 'Independent Lab', 'Inpatient Hospital', 'Office', 
                        'Other', 'Outpatient Hospital', 'Urgent Care'] 
        
    """
    print 'get_all_values(filename=%s, column=%s)' % (filename, column)
    
    column_keys, get_data = common.get_csv(filename)
    assert(column in column_keys[1:])
    
    column_index = column_keys[1:].index(column)
    print 'column_index=%d' % column_index
    
    values = set([])
    for i,(k,v) in enumerate(get_data()):
        #print '%4d:%s %d' % (i,v, len(v))
        values.add(v[column_index])
        if max_num_values > 0:
            if len(values) > max_num_values:
                print 'max_num_values = %d reached' % max_num_values
                break
        
    return sorted(values)

def process_multi_pass(filename, init_func, update_func, prefix, DERIVED_COLUMN_KEYS, NUM_GROUPS = 50):
    """This has got complicated due to python running slowing with large dicts
        Passes through input file multiple times and writes partial results to 
        disk (see group).
        
        init_func() returns the initial value of derived_list 
        update_func(derived_list, input_row) updates derived_list based on input_row
        
        50 may be a better default for NUM_GROUPS (see make_charlson_table())
    """

    print 'process_multi_pass(filename=%s,prefix=%s,DERIVED_COLUMN_KEYS=%s,NUM_GROUPS=%d)' % (filename, 
            prefix, DERIVED_COLUMN_KEYS, NUM_GROUPS)
    
    assert(prefix), 'Need a prefix to avoid over-writing existing files'
    column_keys, get_data = common.get_csv(filename)

    year_column = column_keys[1:].index('Year')

    t0 = time.clock()
    num_rows = 0

    for group in range(NUM_GROUPS):
        derived_dict = {'ALL':{}, 'Y1':{}, 'Y2':{}, 'Y3':{}}
        print 'group=%d of %d' % (group, NUM_GROUPS)
        _, get_data = common.get_csv(filename)
        for k,v in get_data():
            if (int(k) % NUM_GROUPS) != group:
                continue
            year = v[year_column]

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
 
        print ' saving: %d entries' % sum([len(v) for v in derived_dict.values()])        
        pickled_path = make_group_name(group)            
        pkl_file = open(pickled_path , 'wb')
        pickle.dump(derived_dict, pkl_file, -1)   # Pickle data using highest protocol available.
        pkl_file.close()  

    print 'Writing to file'
    for year in sorted(derived_dict.keys()):
        rows_per_year = 0
        derived_filename = '%s%s_%s_%s' % (DERIVED_PREFIX, prefix, year, os.path.basename(filename))
        print 'year=%4s: file=%s' % (year, derived_filename)
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
                rows_per_year += 1
        print ' rows=%d' % rows_per_year        

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
    
def make_key_lut(key_list):
    """Make a look-up table for indexes into key_list
        key_lut[k] = key_list.index(k) + 1
        By convention  key_lut[''] = 0 
    """    
    key_lut = {}
    for i,k in enumerate(key_list):
        key_lut[k] = i+1
    return key_lut
    
def get_key_index(key_lut, key):
    """Return index of key in key_list from which key_lut is constructed. See make_key_lut"""
    if key in key_lut.keys():
        return key_lut[key]
    assert(not key)
    return 0  

def make_primary_condition_group_counts_table(filename):
    """Make the primary condition group table
        PrimaryConditionGroup

    """
    
    prefix = 'pcg'
    derived_column_keys = ['None'] + sorted(PCG_LUT.keys(), key = lambda x: PCG_LUT[x])
    
    column_keys, _ = common.get_csv(filename)
    pcg_column = column_keys[1:].index('PrimaryConditionGroup')

    def init_func():
        return [0 for i in range(len(derived_column_keys))]

    def update_func(derived_list, input_row):
        derived_list[get_pcg_index(input_row[pcg_column])] += 1

    process_multi_pass(filename, init_func, update_func, prefix, derived_column_keys) 

def make_procedure_group_counts_table(filename):
    """
        ProcedureGroup ['', 'ANES', 'EM', 'MED', 'PL', 'RAD', 'SAS', 'SCS', 'SDS', 'SEOA', 'SGS', 
                'SIS', 'SMCD', 'SMS', 'SNS', 'SO', 'SRS', 'SUS']
    """
    PROCEDURE_GROUP_KEYS =  ['ANES', 'EM', 'MED', 'PL', 'RAD', 'SAS', 'SCS', 'SDS', 'SEOA', 'SGS', 
                'SIS', 'SMCD', 'SMS', 'SNS', 'SO', 'SRS', 'SUS']
    prefix = 'proc_group'
    derived_column_keys = ['None'] + sorted(PROCEDURE_GROUP_KEYS)
    key_lut = make_key_lut(PROCEDURE_GROUP_KEYS)
    
    column_keys, _ = common.get_csv(filename)
    column = column_keys[1:].index('ProcedureGroup')

    def init_func():
        return [0 for i in range(len(derived_column_keys))]

    def update_func(derived_list, input_row):
        derived_list[get_key_index(key_lut, input_row[column])] += 1

    process_multi_pass(filename, init_func, update_func, prefix, derived_column_keys)
 
def make_specialty_counts_table(filename):
    """
        Specialty  ['', 'Anesthesiology', 'Diagnostic Imaging', 'Emergency', 'General Practice', 
                    'Internal', 'Laboratory', 'Obstetrics and Gynecology', 'Other', 'Pathology', 
                    'Pediatrics',  'Rehabilitation', 'Surgery']
    """
    SPECIALTY_KEYS = ['Anesthesiology', 'Diagnostic Imaging', 'Emergency', 'General Practice', 
                    'Internal', 'Laboratory', 'Obstetrics and Gynecology', 'Other', 'Pathology', 
                    'Pediatrics',  'Rehabilitation', 'Surgery']
    prefix = 'specialty'
    derived_column_keys = ['None'] + sorted(SPECIALTY_KEYS)
    key_lut = make_key_lut(SPECIALTY_KEYS)
    
    column_keys, _ = common.get_csv(filename)
    column = column_keys[1:].index('Specialty')

    def init_func():
        return [0 for i in range(len(derived_column_keys))]

    def update_func(derived_list, input_row):
        derived_list[get_key_index(key_lut, input_row[column])] += 1

    process_multi_pass(filename, init_func, update_func, prefix, derived_column_keys)

def make_place_service_counts_table(filename):
    """
        PlaceSvc   ['', 'Ambulance', 'Home', 'Independent Lab', 'Inpatient Hospital', 'Office', 
                        'Other', 'Outpatient Hospital', 'Urgent Care']
    """
    PLACE_SVC_KEYS =  ['Ambulance', 'Home', 'Independent Lab', 'Inpatient Hospital', 'Office', 
                        'Other', 'Outpatient Hospital', 'Urgent Care']
    prefix = 'place_svc'
    derived_column_keys = ['None'] + sorted(PLACE_SVC_KEYS)
    key_lut = make_key_lut(PLACE_SVC_KEYS)
    
    column_keys, _ = common.get_csv(filename)
    column = column_keys[1:].index('PlaceSvc')

    def init_func():
        return [0 for i in range(len(derived_column_keys))]

    def update_func(derived_list, input_row):
        derived_list[get_key_index(key_lut, input_row[column])] += 1

    process_multi_pass(filename, init_func, update_func, prefix, derived_column_keys)    
    
def make_charlson_table(filename):
    """CharlsonIndex  ['0', '1-2', '3-4', '5+']
        Use highest Charlson index for any claim for patient in period. Not sure if this is the
        best thing to do
        Wow. This needs process_multi_pass()
    """
    print 'make_charlson_table(filename=%s)' % filename
    
    prefix = 'charlson'
    column_keys, get_data = common.get_csv(filename)
    
    charlson_column = column_keys[1:].index('CharlsonIndex')
    print 'charlson_column=%d' % charlson_column
    
    charlson_func = common.get_int_part
    
    def init_func():
        return [-1]

    def update_func(derived_list, input_row):
        derived_list[0] = max(derived_list[0], charlson_func(input_row[charlson_column]))

    # NUM_GROUPS = 50 if 1.6x faster than 100 which is much faster than 10 for Claims.csv
    process_multi_pass(filename, init_func, update_func, prefix, ['CharlsonIndex'], NUM_GROUPS = 50) 
    
    if False:
        year_column = column_keys[1:].index('Year') 
        charlson_column = column_keys[1:].index('CharlsonIndex')
        print 'year_column=%d' % year_column
        print 'charlson_column=%d' % charlson_column
         
        charlson_func = common.get_int_part
           
        for i,(k,v) in enumerate(get_data()):
            year = v[year_column]
            if not k in derived_dict[year].keys():
                derived_dict[year][k] = -1
            derived_dict[year][k] = max(derived_dict[year][k], charlson_func(v[charlson_column]))
            if (i % 10000) == 0: 
                print 'Processed row %d derived_dict = %s' % (i, 
                    [(kk,len(vv)) for kk,vv in derived_dict.items()])
            
        print 'Read all rows %d' % i    

        for year in sorted(derived_dict.keys()):
            derived_filename = '%s%s_%s' % (DERIVED_PREFIX, year, filename)
            print 'derived_filename=%s' % derived_filename
            f = open(derived_filename , 'wb')
            data_writer = csv.writer(f, delimiter=',', quotechar='"')
            data_writer.writerow(['MemberID', 'CharlsonIndex'])
            for k in sorted(derived_dict[year].keys()):
                x = derived_dict[year][k]
                data_writer.writerow([k] + [str(x)])     
    
def make_lab_counts_table(filename, title):
    """ Used for LabCount.csv and DrugCount.csv which have similar formats"""
    print 'make_lab_counts_table(filename=%s, title=%s)' % (filename, title)
    
    derived_dict = {'Y1':{}, 'Y2':{}, 'Y3':{}}
    column_keys, get_data = common.get_csv(filename)
    year_column = column_keys[1:].index('Year')
    dsfs_column = column_keys[1:].index('DSFS')
    labcount_column = column_keys[1:].index(title)
    print 'year_column=%d' % year_column
    print 'dsfs_column=%d' % dsfs_column
    print 'labcount_column=%d' % labcount_column

    if labcount_column < 0:
        print 'title not matched'
        exit()
  
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
        derived_filename = '%s%s_%s' % (DERIVED_PREFIX, year, filename)
        print 'derived_filename=%s' % derived_filename
        f = open(derived_filename , 'wb')
        data_writer = csv.writer(f, delimiter=',', quotechar='"')
        data_writer.writerow(['MemberID', '%s_DSFS' % title, title])
        for k in sorted(derived_dict[year].keys()):
            row = derived_dict[year][k]
            data_writer.writerow([k] + [str(v) for v in row])     

if __name__ == '__main__':
    import sys
    import optparse

    parser = optparse.OptionParser('python ' + sys.argv[0] + ' options <file name> [<column name>]')
    parser.add_option('-v', '--show-values', action="store_true", dest='show_values', default=False, help='show values of filename column')
    parser.add_option('-c', '--charlson-table', action="store_true", dest='charlson_table', default=False, help='make CharlsonIndex table')
    parser.add_option('-p', '--procedure-group', action="store_true", dest='procedure_group', default=False, help='make procedure_group counts table')
    parser.add_option('-s', '--specialty', action="store_true", dest='specialty', default=False, help='make specialty counts table')
    parser.add_option('-o', '--place-of-service', action="store_true", dest='place_service', default=False, help='make place of service counts table')
    parser.add_option('-g', '--primary-condition-group', action="store_true", dest='primary_condition_group', default=False, help='make primary condition group counts table')
  
    (options, args) =  parser.parse_args()
    
    if len(args) < 1:
        parser.error("Expected 1 argument") 
    
    filename = args[0]
        
    if options.show_values:
        if len(args) < 2:
            parser.error("Expected 2 arguments")  
        column = args[1]
        values = get_all_values(filename, column)
        print '%d values' % len(values)
        print values
        exit()
     
    if options.charlson_table:
        make_charlson_table(filename)  
        exit()
    
    if options.procedure_group:    
        make_procedure_group_counts_table(filename)
        exit()
        
    if options.specialty:    
        make_specialty_counts_table(filename)
        exit()    
    
    if options.place_service:    
        make_place_service_counts_table(filename)
        exit()     
        
    if options.primary_condition_group: 
        make_primary_condition_group_counts_table(filename)
        exit() 

    if 'labcount' in filename.lower() or 'drugcount' in filename.lower():
        title = os.path.splitext(os.path.basename(filename))[0]
        make_lab_counts_table(filename, title) 
        exit()    
       
  
        