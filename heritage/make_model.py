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
from common import AGES, AGE_LOW, AGE_MEDIUM, AGE_HIGH
import select_features

def get_dih_filename(year):
    """Return name of "days in hospital" spreadsheet for specified year"""
    return 'DaysInHospital_Y%d.csv' % year

def get_patient_filename():
    return r'Members.csv'

def get_labcount_filename(year):
    return r'data\derived_Y%d_LabCount.csv' % year

def get_drugcount_filename(year):
    return r'data\derived_Y%d_DrugCount.csv' % year
 
def get_counts_filename(prefix, year):
    return r'data\derived_%s_Y%d_Claims.csv' % (prefix, year)

COUNTS_PREFIXES = ['charlson', 'proc_group', 'specialty', 'place_svc', 'pcg']

def get_pcg_filename(year):
    return get_counts_filename('pcg', year)

def get_procedure_filename(year):
    return get_counts_filename('proc_group', year)
    
def get_specialty_filename(year):
    return get_counts_filename('specialty', year)

def get_place_filename(year):
    return get_counts_filename('place_svc', year)

def get_charlson_filename(year):
    return get_counts_filename('charlson', year)    
    
def get_dih(year):
    """Return "days in hospital" spreadsheet for specified year 
        DaysInHospital_Y?.csv as a dict
    """
    return common.get_dict(get_dih_filename(year), 'DaysInHospital', int)

def get_counts_dict(prefix, year):
    return common.get_dict_all(get_counts_filename(prefix, year), int) 
    
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

def get_labcount_dict(year):
    """Return dict whose keys are MemberIDs and LabCount DSFS and count 
        categories
    """
    return common.get_dict_all(get_labcount_filename(year), int)     
 
def get_drugcount_dict(year):
    """Return dict whose keys are MemberIDs and DrugCount DSFS and count 
        categories
    """
    return common.get_dict_all(get_drugcount_filename(year), int)     

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

def getXy_for_dict(year, keys, counts_dict, threshold):
    """counts_dict[k] and dih_dict[k] countain some input data and dih respectivley for patient k
        For specified year, return X,y wheere
            rows = patients
            columns
                X = contents of counts_dict values
                y = days in hospital > threshold
    """

    dih_dict = get_dih(year)
    dih_keys = set(dih_dict.keys())
    user_keys = sorted(counts_dict.keys())
    
    if False:
        y = np.zeros(len(counts_dict))
        for i,k in enumerate(user_keys):
            y[i] = (k in dih_keys) and (dih_dict[k] > threshold)

    X = np.array([counts_dict[k] for k in user_keys], dtype=float) 
    y = np.array([(k in dih_keys) and (dih_dict[k] > threshold) for k in user_keys])
    
    return X,y 

def getXy_pcg(year, threshold):
    """For specified year, return
        rows = patients
        columns
            X=counts for each pcg class
            y=days in hospital
    """
            
    print 'getXy_pcg(year=%d)' % year
   
    keys, counts_dict = get_pcg_counts_dict(year-1)
    X,y = getXy_for_dict(year, keys, counts_dict, threshold)
    return X,y,keys[1:]

def getXy_patient(year, threshold):
    """For specified year, return
        rows = patients
        columns
            X=age and sex
            y=days in hospital
    """

    print 'getXy_patient(year=%d)' % year

    keys, counts_dict = get_patient_dict()
    X,y = getXy_for_dict(year, keys, counts_dict, threshold)
    return X,y,keys[1:] 

def getXy_all(year, threshold):    
    patient_keys, patient_dict = get_patient_dict()
    pcg_keys, pcg_dict = get_pcg_counts_dict(year-1)
    keys, counts_dict = common.combine_dicts(patient_keys[1:], patient_dict, pcg_keys[1:], pcg_dict)  
    X,y = getXy_for_dict(year, keys, counts_dict, threshold)
    return X,y,keys

def getXy_all_all(year, threshold):    
    """ Should be treating no LabCount and no Drugcount as separate categories
    """
    print 'getXy_all_all(year=%d)' % year

    patient_keys, patient_dict = get_patient_dict()
    keys, counts_dict =  patient_keys[1:], patient_dict
    #print 'patient_dict = %d' % len(counts_dict)

    drug_keys, drug_dict = get_drugcount_dict(year-1)
    keys, counts_dict = common.combine_dicts(keys, counts_dict, drug_keys[1:], drug_dict, use_dict1 = True)
    #print '+drug_dict = %d' % len(counts_dict)

    lab_keys, lab_dict = get_labcount_dict(year-1)
    keys, counts_dict = common.combine_dicts(keys, counts_dict, lab_keys[1:], lab_dict, use_dict1 = True)
    #print '+lab_dict = %d' % len(counts_dict)

    if False:
        pcg_keys, pcg_dict = get_pcg_counts_dict(year-1)
        keys, counts_dict = common.combine_dicts(keys, counts_dict, pcg_keys[1:], pcg_dict)
        print '+pcg_dict = %d' % len(counts_dict)    

    for prefix in COUNTS_PREFIXES:
        pre_keys, pre_dict = get_counts_dict(prefix, year-1)
        pre_keys = ['%s=%s' % (prefix, k) for k in pre_keys]
        keys, counts_dict = common.combine_dicts(keys, counts_dict, pre_keys[1:], pre_dict)
        #print '+%s_dict = %d' % (prefix, len(counts_dict)) 
    
    X,y = getXy_for_dict(year, keys, counts_dict, threshold)
    return X,y,keys

# Remove columns with counts below this threshold
LOW_COUNT_THRESHOLD = 100   


def getXy_by_features_(year, features, threshold):
    """Return X,y for year, features and age
        Age in AGES for 3 three groups
        year = -1 => all years
        age = None => all ages
    """
    print 'getXy_by_features(year=%d,features=%s,threshold=%d)' % (year, features, threshold)
    
    def get_by_year(year):
        assert(year > 0)
        if features == 'pcg':
            X,y,keys = getXy_pcg(year, threshold)
        elif features == 'patient':
            X,y,keys = getXy_patient(year, threshold)  

        elif features == 'all':
            X,y,keys = getXy_all(year, threshold)
        elif features == 'all2':
            X,y,keys = getXy_all_all(year, threshold)

        return X,y,keys

    if year > 0:
        X,y,keys = get_by_year(year)
    else:
        X2,y2,keys = get_by_year(2)
        X3,y3,keys = get_by_year(3)
        X = np.r_[X2, X3]
        y = np.r_[y2, y3]
    
    return X,y,keys
    
def filter_by_keys(X, keys, filter_keys):
    """Filter X,keys by filter_keys
        X is a matrix, 
        keys are names of X columns
        filter_keys uses the same names as keys
    """
    filter_indexes = [(k in filter_keys) for k in keys]
    
    print 'X=%s,filter_indexes=%s' % (X.shape, len(filter_indexes))
    Xout = X[:, np.array(filter_indexes)]
    kout = [k for k in keys if k in filter_keys]
    print 'Xout=%s,kout=%s' % (Xout.shape, len(kout))
    return Xout, kout

def getXy_by_sex_age(X,y,keys, sex, age, sex_boundary = 0.5, age_boundaries = [1, 79]):
    print 'getXy_by_sex_age(X=%s,y=%s,sex=%s,age=%s' % (X.shape, y.shape, sex, age)

    if sex and sex.lower()[0] in 'mf' and 'Sex' in keys:
        # Get male or female population
        sex_key = keys.index('Sex')
        if sex.lower()[0] == 'm':
            p = X[:,sex_key] < sex_boundary
        else:    
            p = X[:,sex_key] > sex_boundary

        X = X[p,:]
        y = y[p]
        print 'sex=%s => X=%s,y=%s' % (sex, X.shape, y.shape)

    if age in AGES and 'AgeAtFirstClaim' in keys:
        # Get population for age group
        # python reduce.py -v Members.csv AgeAtFirstClaim        
        # ['', '0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
        age_key = keys.index('AgeAtFirstClaim')
        if age == AGE_LOW:
            p = X[:,age_key] < age_boundaries[0]
        elif age == AGE_HIGH:    
            p = X[:,age_key] > age_boundaries[1]
        else:    
            p = (X[:,age_key] > age_boundaries[0]) & (X[:,age_key] < age_boundaries[1])    

        X = X[p,:]
        y = y[p] 
        print 'age=%s => X=%s,y=%s' % (age, X.shape, y.shape)
        print 'Ages min=%d,max=%d' % (X[:,age_key].min(), X[:,age_key].max())

    # Remove columns with low counts
    Xtot = X.sum(axis=0)
    significant = Xtot >= LOW_COUNT_THRESHOLD
    # Remove sex too, as we are selecting on it
    significant[sex_key] = False
    
    # age only has one value in these cases
    if age == AGE_LOW or age == AGE_HIGH:
        significant[age_key] = False
    
    #print 'Removing keys < %d: %s' % (LOW_COUNT_THRESHOLD, [keys[i] for i in range(len(keys)) if not significant[i]])
    #print 'keys=%d X=%s => ' % (len(keys), X.shape),    
    keys = [keys[i] for i in range(len(keys)) if significant[i]]
    X = X[:,significant] 
    #print 'keys=%d X=%s' % (len(keys), X.shape) 

    return X,y,keys

def normalize(X, y):
    # Normalize
    means = X.mean(axis=0)
    stds = X.std(axis=0)

    for i in range(X.shape[1]):
        X[:,i] = X[:,i] - means[i]
        if abs(stds[i]) > 1e-6:
            X[:,i] = X[:,i]/stds[i]    

    return X,y
    
def getXy_by_features(year, features, sex, age = None):
    """Return X,y for year, features and age
        Age in AGES for 3 three groups
        year = -1 => all years
        age = None => all ages
    """
    print 'getXy_by_features(year=%d,features=%s,sex=%s,age=%s)' % (year, features, sex, age)
    
    X,y,keys = getXy_by_features_(year, features)
    X,y,keys = getXy_by_sex_age(X,y,keys, sex, age)
    X,y = normalize(X, y)

    return X,y,keys  

def find_best_features(year, features, sex, age, heavy):
    """year=-1 => both years 2,3 """
    print 'find_best_features(year=%d,features=%s,sex=%s,age=%s,heavy=%s)' % (year, features, sex,
        age, heavy)
    X, y, keys = getXy_by_features(year, features, sex, age)
    title = 'features=%s,sex=%s,age=%s,year=%d' % (features,sex,age,year) 
    results, n_samples = select_features.get_most_predictive_feature_set(title, X, y, keys, heavy)
    return results, n_samples, keys  

def compare_sexes(year):
    print 'compare_sexes(year=%d)' % year
    X,y,keys = getXy_all(year)
    print 'keys = %s' % ['%d:%s'%(i,k) for i,k in enumerate(keys)]
    
    # Get male or female population
    sex_key = keys.index('Sex')
    m = X[:,sex_key] < 0.5
    f = X[:,sex_key] > 0.5

    Xm = X[m,:].sum(axis=0)
    Xf = X[f,:].sum(axis=0)
    
    common.SUBHEADING()
    print 'year = %d' % year
    print '%20s, %7s, %7s' % ('key', 'male', 'female')
    for k in keys:
        i = keys.index(k)
        t = Xm[i] + Xf[i]
        sgn = ''
        if Xf[i]/t < 0.3:
            sgn = '<'
        if Xf[i]/t > 0.7:
            sgn = '>'    
        print '%20s, %7d, %7d %.2f %.2f %s' % (k, Xm[i], Xf[i], Xm[i]/t, Xf[i]/t, sgn) 

def make_predictions(year, features, sex):
    import predict
    PREDICTIVE_INDICES = [0, 25, 43, 65]
    print 'make_predictions(year=%d)' % year
    X, y, keys = getXy_by_features(year, features, sex)
    X = X[:,PREDICTIVE_INDICES]
    keys = [keys[i] for i in PREDICTIVE_INDICES]
    predict.classify('sex=%s_year=%d' % (sex,year), X, y, keys)
    
def compare_classifiers(year, features, sex):
    import predict
    PREDICTIVE_INDICES = [0, 25, 43, 65]
    print 'compare_classifiers(year=%d)' % year
    X, y, keys = getXy_by_features(year, features, sex)
    X = X[:,PREDICTIVE_INDICES]
    keys = [keys[i] for i in PREDICTIVE_INDICES]
    predict.compare_classifiers('sex=%s_year=%d' % (sex,year), X, y, keys)    



def model_by_threshold(X,y,keys, threshold):
    import os
    import random
    from sklearn import metrics
    from sklearn.cross_validation import StratifiedKFold
    import ga
    import predict
    
    DO_TOP_FEATURES = True
    if DO_TOP_FEATURES:
        top_features = {'m':{}, 'f':{}}
        top_features['m'][AGE_LOW] = ['specialty=Surgery', 'place_svc=Independent Lab', 'place_svc=Urgent Care', 'pcg=INFEC4', 'pcg=MISCL5', 'pcg=SKNAUT']
        top_features['m'][AGE_MEDIUM] = ['pcg=CANCRA', 'pcg=MISCHRT', 'pcg=NEUMENT', 'pcg=ODaBNCA', 'pcg=SKNAUT', 'pcg=TRAUMA', 'pcg=UTI'] 
        top_features['m'][AGE_HIGH] = ['LabCount', 'proc_group=RAD', 'place_svc=Office', 'pcg=ARTHSPIN', 'pcg=FLaELEC', 'pcg=RENAL2']
        top_features['f'][AGE_LOW] = ['charlson=CharlsonIndex', 'proc_group=MED', 'place_svc=Inpatient Hospital', 'place_svc=Office', 'pcg=HEMTOL', 'pcg=MISCL5', 'pcg=SKNAUT']
        top_features['f'][AGE_MEDIUM] = ['pcg=CHF', 'pcg=METAB1', 'pcg=MSC2a3', 'pcg=PERVALV', 'pcg=RENAL3', 'pcg=ROAMI']
        top_features['f'][AGE_HIGH] = ['DrugCount_DSFS', 'proc_group=SDS', 'specialty=None', 'pcg=MISCL5', 'pcg=NEUMENT', 'pcg=ODaBNCA', 'pcg=SKNAUT', 'pcg=TRAUMA']
   
   # Set random seed so that each run gives same results
    random.seed(333)
    np.random.seed(333)

    def P(s):
        """Print string s"""
        print s
        #logfile.write(s + '\n')
        
       
    Xr, yr = select_features.resample_equal_y(X, y, 1.0)
    Xr, yr = normalize(Xr, yr)

    sex_vals = np.unique(Xr[:,keys.index('Sex')])
    age_vals = np.unique(Xr[:,keys.index('AgeAtFirstClaim')])
    sex_boundary = sex_vals.mean()
    age_boundaries = [0.5*(age_vals[i]+age_vals[i+1]) for i in [0,age_vals.size-2]] 
    print 'sex_vals = %s' % sex_vals
    print 'age_vals = %s' % age_vals
    print 'sex_boundary = %s' % sex_boundary
    print 'age_boundaries = %s' % age_boundaries

        
    def make_classifier(X_train, y_train):
        classifier = predict.CompoundClassifier(keys, 'Sex', 'AgeAtFirstClaim', 
            sex_boundary, age_boundaries)
      
        for sex in ['f', 'm']:
            for age in AGES:
                Xsa,ysa, ksa = getXy_by_sex_age(X_train, y_train, keys, sex, age, sex_boundary, 
                    age_boundaries)
                if DO_TOP_FEATURES:
                    # Use only the best X columns
                    #filtered_featurs = ['Sex', 'AgeAtFirstClaim']
                    assert(Xsa.shape[1] == len(ksa))
                    Xsa,ksa= filter_by_keys(Xsa, ksa, top_features[sex][age])
                    assert(Xsa.shape[1] == len(ksa))
                    
                print 'Xsa=%s,Xsa=%s,ksa=%d' % (Xsa.shape, ysa.shape, len(ksa))
                classifier.train(Xsa, ysa, ksa, sex, age)

        classifier.show_all() 
        return classifier

    print 'Xr=%s,yr=%s' % (Xr.shape, yr.shape)
    NUM_FOLDS = 2
    skf = StratifiedKFold(yr, NUM_FOLDS)    
        
    y_test_all = np.zeros(0)
    y_pred_all = np.zeros(0)
    
    for i,(train, test) in enumerate(skf):
        X_train, y_train = Xr[train,:], yr[train]
        X_test, y_test = Xr[test,:], yr[test]

        print 'X_train=%s,y_train=%s' % (X_train.shape, y_train.shape)

        common.SUBHEADING()
        P('Fold %d of %d' % (i, NUM_FOLDS))
        P('classify: X_train=%s, y_train=%s' % (X_train.shape, y_train.shape))
        P('classify:  X_test=%s,  y_test=%s' % (X_test.shape, y_test.shape))
        
        if True:
            classifier = make_classifier(X_train, y_train)
        else:
            classifier = predict.CompoundClassifier(keys, 'Sex', 'AgeAtFirstClaim', 
                sex_boundary, age_boundaries)
          
            for sex in ['f', 'm']:
                for age in AGES:
                    Xsa,ysa, ksa = getXy_by_sex_age(X_train, y_train, keys, sex, age, sex_boundary, 
                        age_boundaries)
                    if DO_TOP_FEATURES:
                        # Use only the best X columns
                        #filtered_featurs = ['Sex', 'AgeAtFirstClaim']
                        assert(Xsa.shape[1] == len(ksa))
                        Xsa,ksa= filter_by_keys(Xsa, ksa, top_features[sex][age])
                        assert(Xsa.shape[1] == len(ksa))
                        
                    print 'Xsa=%s,Xsa=%s,ksa=%d' % (Xsa.shape, ysa.shape, len(ksa))
                    classifier.train(Xsa, ysa, ksa, sex, age)

            classifier.show_all()

        y_pred = classifier.predict(X_test, keys)

        P('Classification report for classifier %s:\n%s\n' % (classifier, 
                    metrics.classification_report(y_test, y_pred)))

        y_test_all = np.r_[y_test_all, y_test]
        y_pred_all = np.r_[y_pred_all, y_pred]    

    common.HEADING()
    print 'Classification report for all %s:\n%s\n' % (
                    classifier, metrics.classification_report(y_test_all, y_pred_all))
    print 'Confusion matrix:\n%s' % metrics.confusion_matrix(y_test_all, y_pred_all)
    
    
if __name__ == '__main__':
        
    features = 'all2'
    threshold = 0
    X,y,keys = getXy_by_features_(-1, features, threshold)
    model_by_threshold(X, y, keys, threshold)
    exit()
    for threshold in [0,1,2,4,8,16]:
        X0,y0,X1,y1 = model_by_threshold(X,y,keys,threshold)
        X = X1
        y = y1
    