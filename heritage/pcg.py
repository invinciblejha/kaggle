from __future__ import division
"""
  Find which pcg keys correlate with {DIH==0|DIH!=0}

"""
import time
import csv
import numpy as np
import pylab as pl
from sklearn.linear_model import SGDClassifier
import common

def get_dih_filename(year):
    """Return name of "days in hospital" spreadsheet for specified year"""
    return 'DaysInHospital_Y%d.csv' % year

def get_patient_filename():
    return r'Members.csv'
    
def get_pcg_filename(year):
    return r'data\derived_all_counts_Y%d_Claims.csv' % year
    
def get_dih(year):
    """Return "days in hospital" spreadsheet for specified year 
        DaysInHospital_Y?.csv as a dict
    """
    return common.get_dict(get_dih_filename(year), 'DaysInHospital', int)

    
def get_pcg_counts_dict(year):
    """Return dict whose keys are MemberIDs and values are PCG counts for all the PCG 
        categories
    """
    return common.get_dict_all(get_pcg_filename(year), int) 
    
def get_patient_dict():
    """Return dict whose keys are MemberIDs and patient sex and age 
        categories
    """
    return common.get_dict_all(get_patient_filename(), None)     

def get_total_pcg_filename(year):
    return r'data\pcg_totals_Y%d_Claims.csv' % year    

def show_totals_by_dih(year):
    print 'show_totals_by_dih(year=%d)' % year
    
    dih_dict = get_dih(year)
    dih_dict_keys = set(dih_dict.keys())
    pcg_keys, pcg_counts_dict = get_pcg_counts_dict(year-1)
    print 'got dicts %d x %d' % (len(pcg_counts_dict), len(pcg_keys))
    
    user_keys = sorted(pcg_counts_dict.keys())
    has_dih_keys = np.zeros(len(pcg_counts_dict))
    has_no_dih_keys = np.zeros(len(pcg_counts_dict))
    for i in range(len(has_dih_keys)):
        k = user_keys[i]
        if (k in dih_dict_keys):
            if dih_dict[k] > 0:
                has_dih_keys[i] = 1
            else:
                has_no_dih_keys[i] = 1 
    
    pcg_counts_a = np.array([pcg_counts_dict[k] for k in user_keys]) 
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

if False:
    TOP_PCG_KEYS_TEXT = '''RENAL2	HIPFX	CHF	AMI	RENAL1	FLaELEC	PRGNCY	HEMTOL	ROAMI	SEPSIS	PNCRDZ	STROKE	HEART2	CANCRA'''
    TOP_PCG_KEYS = [s.strip() for s in TOP_PCG_KEYS_TEXT.split('\t')]
    print TOP_PCG_KEYS
    exit()
TOP_PCG_KEYS = ['RENAL2', 'HIPFX', 'CHF', 'AMI', 'RENAL1', 'FLaELEC', 'PRGNCY', 'HEMTOL', 'ROAMI', 
    'SEPSIS', 'PNCRDZ', 'STROKE', 'HEART2', 'CANCRA']

def classify_nn(X, y, k):
    m = X.shape[0]
    m_test = int(m*0.25)
    m_train = m - m_test
 
    # Split data in train and test data
    # A random permutation, to split the data randomly
    #np.random.seed(k)
    indices = np.random.permutation(m)
    X_train = X[indices[:m_train]]
    y_train = y[indices[:m_train]]
    X_test  = X[indices[m_train:]]
    y_test  = y[indices[m_train:]]
    
    # Create and fit a nearest-neighbor classifier
    from sklearn.neighbors import NeighborsClassifier
    knn = NeighborsClassifier()
    knn.fit(X_train, y_train)
    print 'knn=%s' % knn
    y_pred = knn.predict(X_test)
    correct = y_pred == y_test
    print 'k=%2d: Num tests=%6d correct=%6d = %2d%%' % (k, correct.shape[0], correct.sum(),
                int(100*correct.sum()/correct.shape[0]))
    if False:
        for i in range(correct.shape[0]):
            print '  %d==%d => %d' % (y_pred[i], y_test[i], correct[i])
        exit()    

def classify(X, y):   
    print 'classify(X=%s,Y=%s)' % (X.shape, y.shape)
   
    # Normalize
    means = X.mean(axis=0)
    stds = X.std(axis=0)
    if False:
        print '    X:', X.shape, X[0,:]
        print 'means:', means.shape, means
        print ' stds:', stds.shape, stds
    
    for i in range(X.shape[1]):
        X[:,i] = X[:,i] - means[i]
        if abs(stds[i]) > 1e-4:
            X[:,i] = X[:,i]/stds[i]
        
    if False:
        means = X.mean(axis=0)
        stds = X.std(axis=0)
        print 'After normalization'
        print '    X:', X.shape, X[0,:]
        print 'means:', means.shape, means
        print ' stds:', stds.shape, stds
   
    for k in [1,5,20]:
        for i in range(5):
            classify_nn(X,y,k)
        common.SUBHEADING()
    if False:    
        for k in range(1,200):
            for i in range(10):
                classify_nn(X,y,k)
            common.SUBHEADING()    
        exit()
    
    if False:
        X = Xa.tolist()
        y = ya.tolist()
        print 'X: %dx%d' %(len(X),len(X[0]))
        print 'y: %d' %(len(y))
        
        
        if False:
            X2 = []
            Y2 = []
            
            for i in range(len(X)):
                if any(X[i]):
                    print 'X[%d]:%s' %(i,X[i])
                    print 'Y[%d]:%s' %(i,Y[i])
                    X2.append(X[i])
                    Y2.append(Y[i])
            X = X2
            Y = Y2
            
        # fit the model
        clf = SGDClassifier(loss="hinge", alpha = 0.01, n_iter=50) #, fit_intercept=True)
        clf.fit(X, Y)

        # plot the line, the points, and the nearest vectors to the plane
        xx = np.linspace(-5, 5, 10)
        yy = np.linspace(-5, 5, 10)
        X1, X2 = np.meshgrid(xx, yy)
        Z = np.empty(X1.shape)
        for (i,j), val in np.ndenumerate(X1):
            x1 = val
            x2 = X2[i,j]
            p = clf.decision_function([x1, x2])
            Z[i,j] = p[0]
        levels = [-1.0, 0.0, 1.0]
        linestyles = ['dashed','solid', 'dashed']
        colors = 'k'
        pl.set_cmap(pl.cm.Paired)
        pl.contour(X1, X2, Z, levels, colors=colors, linestyles=linestyles)
        pl.scatter(X[:,0], X[:,1], c=Y)
    
def show_dih_counts(year):
    print 'show_dih_counts(year=%d)' % year
    
    pcg_filename = get_pcg_filename(year-1)
    print 'pcg_filename=%s' % pcg_filename
    
    dih_dict = get_dih(year)
    dih_dict_keys = set(dih_dict.keys())
    member_ids = common.get_member_ids(pcg_filename)
    print '%d claims' % len(member_ids)
    
    pcg_keys, pcg_counts_dict = get_pcg_counts_dict(year-1)
    print 'got dicts %d x %d' % (len(pcg_counts_dict), len(pcg_keys))
       
    user_keys = sorted(pcg_counts_dict.keys())
    has_dih_keys = np.zeros(len(pcg_counts_dict))
    has_no_dih_keys = np.zeros(len(pcg_counts_dict))
    for i in range(len(has_dih_keys)):
        k = user_keys[i]
        if (k in dih_dict_keys):
            if dih_dict[k] > 0:
                has_dih_keys[i] = 1
            else:
                has_no_dih_keys[i] = 1 
    
    pcg_counts_a = np.array([pcg_counts_dict[k] for k in user_keys]) 
    pcg_counts_a = pcg_counts_a.astype(float)
    print 'converted to numpy array'
    print 'pcg_counts_a.shape', pcg_counts_a.shape 
    
    column_keys,_ = common.get_csv(get_pcg_filename(year))
    for num_keys in range(1,len(TOP_PCG_KEYS)+1):
        for key0 in range((num_keys+1)//2):
            common.HEADING()
            print 'Testing keys %s %d %d' % (TOP_PCG_KEYS[key0:num_keys], key0, num_keys)
            idxs = [column_keys[1:].index(key) for key in TOP_PCG_KEYS[:num_keys]]
            X = pcg_counts_a[:,idxs]
            Y = has_dih_keys
            classify(X, Y)


def getXy_for_dict(year, pcg_keys, counts_dict):
    """For specified year, return
        rows = patients
        columns
            X=counts for each pcg class
            y=days in hospital
    """

    print 'getXy_for_dict(year=%d) dict= %d x %d' % (year, len(counts_dict), len(pcg_keys))

    dih_dict = get_dih(year)

    # This seeems to be necessary. Not sure why
    dih_dict_keys = set(dih_dict.keys())

    user_keys = sorted(counts_dict.keys())
    has_dih = np.zeros(len(counts_dict))
    # We don't use has_no_dih!
    has_no_dih = np.zeros(len(counts_dict))
    for i in range(len(counts_dict)):
        k = user_keys[i]
        if k in dih_dict_keys:
            if dih_dict[k] > 0:
                has_dih[i] = 1
            else:
                has_no_dih[i] = 1 

    counts_list = [counts_dict[k] for k in user_keys]
    print 'counts_list[0] = ', len(counts_list), counts_list[0], type(counts_list[0]), type(counts_list[0][0]) 
    counts = np.array(counts_list, dtype=float) 
    print 'counts:', counts.shape 
   
    X = counts
    y = has_dih
   
    return X,y 

def getXy_pcg(year):
    """For specified year, return
        rows = patients
        columns
            X=counts for each pcg class
            y=days in hospital
    """
            
    print 'getXy_pcg(year=%d)' % year
   
    keys, counts_dict = get_pcg_counts_dict(year-1)
    X,y = getXy_for_dict(year, keys, counts_dict)
    return X,y,keys

def getXy_patient(year):
    """For specified year, return
        rows = patients
        columns
            X=age and sex
            y=days in hospital
    """

    print 'getXy_patient(year=%d)' % year

    keys, counts_dict = get_patient_dict()
    X,y = getXy_for_dict(year, keys, counts_dict)
    return X,y,keys 

def getXy_all(year):    
    patient_keys, patient_dict = get_patient_dict()
    pcg_keys, pcg_dict = get_pcg_counts_dict(year-1)
    keys, counts_dict = common.combine_dicts(patient_keys, patient_dict, pcg_keys, pcg_dict)  
    X,y = getXy_for_dict(year, keys, counts_dict)
    return X,y,keys
    
def find_best_features(year, features, sex):
    import select_features
    print 'find_best_features(year=%d)' % year
    if features == 'pcg':
        X,y,keys = getXy_pcg(year)
    elif features == 'patient':
        X,y,keys = getXy_patient(year)  
               
    elif features == 'all':
        X,y,keys = getXy_all(year)
    
    if sex and sex.lower()[0] in 'mf' and 'Sex' in keys:
        # Get male or female population
        sex_key = keys[1:].index('Sex')
        if sex.lower()[0] == 'm':
            p = X[:,sex_key] < 0.5
        else:    
            p = X[:,sex_key] > 0.5

        X = X[p,:]
        y = y[p]

     # Normalize
    means = X.mean(axis=0)
    stds = X.std(axis=0)

    for i in range(X.shape[1]):
        X[:,i] = X[:,i] - means[i]
        # Be careful not to increase variance of nearly constant variables
        if abs(stds[i]) > 1e-1:
            X[:,i] = X[:,i]/stds[i]    
    
    return select_features.get_most_predictive_feature_set(X, y), keys  

def make_predictions(year):
    import predict
    PREDICTIVE_INDICES = [1, 3, 12, 23, 26, 27, 28, 34, 37, 40]
    print 'make_predictions(year=%d)' % year
    X,y = getXy_pcg(year)
    X = X[:,PREDICTIVE_INDICES]
    predict.predict(X,y)

if False:    
    show_totals_by_dih(2)            
    show_totals_by_dih(3)    
 
if False:
    show_dih_counts(2)
    show_dih_counts(3)

if True:
    import random
     # Set random seed so that each run gives same results
    random.seed(333)
    np.random.seed(333)
    
    #features = 'patient'
    #features = 'pcg'
    features = 'all'
    
    def show_result(results, keys, j):
        r = results[j]
        decoded_genome = [keys[g+1] for g in r['genome']]
        print '%6d: %.3f %s %s' % (j, r['score'], r['genome'], decoded_genome)
        
    all_results = {}
    for sex in ['f', 'm']:
        all_results[sex] = {}
        for year in (2,3):
            common.SUBHEADING()
            print 'sex = %s, year = %d' % (sex, year)
            all_results[sex][year], keys = find_best_features(year, features, sex)
            results = all_results[sex][year]
            for j in sorted(results.keys()):
                show_result(results, keys, j) 
    common.HEADING()    
    for sex in sorted(all_results.keys()):
        for year in sorted(all_results[sex].keys()):
            print 'sex = %s, year = %d' % (sex, year)
            results = all_results[sex][year]
            for j in sorted(results.keys()):
                show_result(results, keys, j)        
            
if False:
    for year in (3,2):
        make_predictions(year)            