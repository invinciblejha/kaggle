from __future__ import division
"""
    Explore Heritage .csv files
"""
import math
import os
import random
import re
import csv

def get_csv(path):
    data_reader = csv.reader(open(path , 'rb'), delimiter=',', quotechar='"')
    column_keys = data_reader.next()
    
    def get_data():
        for row in data_reader:
            patient_key = row[0]
            data = row[1:]
            yield(patient_key, data)
            
    return column_keys, get_data
    
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

def get_dict(filename, key=None, xform=int):
    column_keys, get_data = get_csv(filename)
    if not key:
        return column_keys
    
    print 'filename=%s, key=%s, column_keys=%s' % (filename, key, column_keys)
    assert(key in column_keys[1:])
    column = column_keys[1:].index(key)
    data_dict = {}
    for k,v in get_data():
        x = xform(v[column])
        if x is not None:
            data_dict[k] = x
    return column_keys, data_dict

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

def get_annotated_data(filename, key=None, xform=int):
    column_keys, data_dict = get_dict(filename, key, xform)
    return {'filename':filename, 'column':key, 'data':data_dict}
 
def jitter(x,y):
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
    
def plot_outcomes_vs_counts(annotated_data_x, annotated_data_y):
    import matplotlib.pyplot as plt
   
    data_x = annotated_data_x['data']
    data_y = annotated_data_y['data']
    label_x = '%s:%s'%(annotated_data_x['filename'], annotated_data_x['column'])
    label_y = '%s:%s'%(annotated_data_y['filename'], annotated_data_y['column'])
    
    summarize(label_x, data_x.values())
    summarize(label_y, data_y.values())
    
    keys = set(data_x.keys()) & set(data_y.keys())
    x = [data_x[k] for k in keys]
    y = [data_y[k] for k in keys] 
    x,y = jitter(x,y)
    
    for ad,z in ((annotated_data_x,x), (annotated_data_y,y)):
        summarize('%s:%s'%(ad['filename'], ad['column']), z)
    plt.scatter(x, y, s=1,  lw = 0)
    
    plt.xlabel('%s:%s'%(annotated_data_x['filename'], annotated_data_x['column']))
    plt.ylabel('%s:%s'%(annotated_data_y['filename'], annotated_data_y['column']))
    plt.show()
    
if __name__ == '__main__':
    import sys
    import optparse

    parser = optparse.OptionParser('python ' + sys.argv[0] + ' options <file name>')
    #parser.add_option('-r', '--ratio', dest='ratio', default='1.0', help='resampling ratio')
    (options, args) = parser.parse_args()
    
    #_, outcomes_dict = get_outcomes_dict()
    #_, members_dict = get_members_dict()
    
    ad_age_at_first_claim = get_annotated_data(MEMBERS_FILE, 'AgeAtFirstClaim', get_member_age)
    ad_days_in_hospital = get_annotated_data(OUTCOMES_FILE, 'DaysInHospital')
    
    #show_counts(path)
    plot_outcomes_vs_counts(ad_age_at_first_claim, ad_days_in_hospital)
    
   
    