from __future__ import division
"""
  Find which pcg keys correlate with {DIH==0|DIH!=0}

"""
import time
import csv
import numpy as np
import common

def get_dih_filename(year):
    return 'DaysInHospital_Y%d.csv' % year

def get_dih(year):
    return common.get_dict(get_dih_filename(year), 'DaysInHospital', int)

def get_pcg_filename(year):
    return r'data\derived_all_counts_Y%d_Claims.csv' % year
    
def get_pcg_counts(year):
    return common.get_dict_all(get_pcg_filename(year), int) 
    
def get_total_pcg_filename(year):
    return r'data\pcg_totals_Y%d_Claims.csv' % year    

def show_dih_correlation(year):
    print 'show_dih_correlation(year=%d)' % year
    
    dih_dict = get_dih(year)
    dih_dict_keys = set(dih_dict.keys())
    pcg_keys, pcg_counts = get_pcg_counts(year-1)
    print 'got dicts %d x %d' % (len(pcg_counts), len(pcg_keys))
    
    user_keys = sorted(pcg_counts.keys())
    has_dih_keys = np.zeros(len(pcg_counts))
    has_no_dih_keys = np.zeros(len(pcg_counts))
    for i in range(len(has_dih_keys)):
        k = user_keys[i]
        if (k in dih_dict_keys):
            if dih_dict[k] > 0:
                has_dih_keys[i] = 1
            else:
                has_no_dih_keys[i] = 1 
    
    if False:
        tmp = [pcg_counts[k] for k in user_keys[:3]]
        print tmp
        tmpa = np.array(tmp)
        print tmpa
        
    pcg_counts_a = np.array([pcg_counts[k] for k in user_keys]) 
    print 'converted to numpy array'
    print 'pcg_counts_a.shape', pcg_counts_a.shape 
      
    pcg_counts_a_has_dih = pcg_counts_a.compress(has_dih_keys > 0, axis=0)
    print 'Stripped rows with DIH values'
    print 'pcg_counts_a.shape', pcg_counts_a_has_dih.shape

    pcg_counts_a_has_no_dih = pcg_counts_a.compress(has_no_dih_keys > 0, axis=0)
    print 'Stripped rows without DIH values'
    print 'pcg_counts_a.shape', pcg_counts_a_has_no_dih.shape
    
    print 'rows used = %d of %d' % (pcg_counts_a_has_dih.shape[0] + pcg_counts_a_has_no_dih.shape[0],
            pcg_counts_a.shape[0]) 
           
    mean_all = np.mean(pcg_counts_a, axis = 0)
    mean_has_dih = np.mean(pcg_counts_a_has_dih, axis = 0)       
    mean_has_no_dih = np.mean(pcg_counts_a_has_no_dih, axis = 0)
    
    totals_filename = get_total_pcg_filename(year)
    data_writer = csv.writer(open(totals_filename , 'wb'), delimiter=',', quotechar='"')
    data_writer.writerow(pcg_keys)
    data_writer.writerow(['mean_all'] + [str(v) for v in mean_all])
    data_writer.writerow(['mean_has_no_dih'] + [str(v) for v in mean_has_no_dih])
    data_writer.writerow(['mean_has_dih'] + [str(v) for v in mean_has_dih])
        
show_dih_correlation(2)            
show_dih_correlation(3)    
        
    