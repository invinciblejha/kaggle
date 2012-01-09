from __future__ import division
"""
    A prediction model for the Heritage health prize
    Prediction is by cascading classifiers
 

"""
import math
import time
import csv
import numpy as np
import pylab as pl

import sklearn
from sklearn import svm, metrics, linear_model
#from sklearn.metrics import roc_curve, auc
#from sklearn.cross_validation import StratifiedKFold

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

def getXy_for_dict(year, keys, counts_dict):
    """counts_dict[k] and dih_dict[k] countain some input data and dih respectivley for patient k
        For specified year, return X,y wheere
            rows = patients
            columns
                X = contents of counts_dict values
                y = days in hospital 
    """

    dih_dict = get_dih(year)
    dih_keys = set(dih_dict.keys())
    user_keys = sorted(counts_dict.keys())

    X = np.array([counts_dict[k] for k in user_keys], dtype=float) 
    y = np.array([dih_dict[k] if k in dih_keys else 0 for k in user_keys])
    
    return X,y 

def getXy_pcg(year,):
    """For specified year, return
        rows = patients
        columns
            X=counts for each pcg class
            y=days in hospital
    """
            
    print 'getXy_pcg(year=%d)' % year
   
    keys, counts_dict = get_pcg_counts_dict(year-1)
    X,y = getXy_for_dict(year, keys, counts_dict)
    return X,y,keys[1:]

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
    return X,y,keys[1:] 

def getXy_all(year):    
    patient_keys, patient_dict = get_patient_dict()
    pcg_keys, pcg_dict = get_pcg_counts_dict(year-1)
    keys, counts_dict = common.combine_dicts(patient_keys[1:], patient_dict, pcg_keys[1:], pcg_dict)  
    X,y = getXy_for_dict(year, keys, counts_dict)
    return X,y,keys

def getXy_all_all(year):    
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

    for prefix in COUNTS_PREFIXES:
        pre_keys, pre_dict = get_counts_dict(prefix, year-1)
        pre_keys = ['%s=%s' % (prefix, k) for k in pre_keys]
        keys, counts_dict = common.combine_dicts(keys, counts_dict, pre_keys[1:], pre_dict)
        #print '+%s_dict = %d' % (prefix, len(counts_dict)) 
    
    X,y = getXy_for_dict(year, keys, counts_dict)
    return X,y,keys

# Remove columns with counts below this threshold
LOW_COUNT_THRESHOLD = 100   

def getXy_by_features_(year, features):
    """Return X,y for year, features and age
        Age in AGES for 3 three groups
        year = -1 => all years
        age = None => all ages
    """
    print 'getXy_by_features(year=%d,features=%s)' % (year, features)
    
    def get_by_year(year):
        assert(year > 0)
        if features == 'pcg':
            X,y,keys = getXy_pcg(year)
        elif features == 'patient':
            X,y,keys = getXy_patient(year)  

        elif features == 'all':
            X,y,keys = getXy_all(year)
        elif features == 'all2':
            X,y,keys = getXy_all_all(year)

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

    keys = [keys[i] for i in range(len(keys)) if significant[i]]
    X = X[:,significant] 

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

    
def get_accuracy_(y_test, y_pred):
    """http://www.heritagehealthprize.com/c/hhp/details/Evaluation
    """
    m = y_test.size
    assert(y_pred.size == m)
    d = np.zeros(m)
    for i in range(m):
        d[i] = (math.log(y_pred[i]+1) - math.log(y_test[i]+1))**2
    return math.sqrt(d.sum()/m)

def get_accuracy(y_test, y_pred):    
    u_test = np.unique(y_test)
    u_pred = np.unique(y_pred)
    print 'u_test=%s' % u_test
    print 'u_pred=%s' % u_pred
    
    for v in sorted(u_pred):
        f = (y_pred == v)
        a = get_accuracy_(y_test[f], y_pred[f])
        print ' accuracy y_pred=%s = %f' % (v, a)
    return get_accuracy_(y_test, y_pred)
    
def get_trained_classifier(X, y, keys):
    """Return classifier trained on X and y
       X columns are typically a subset of a bigger X
       y is a boolean array
       No resampling as this is for part of a data set
       NOTE use of "class_weight = 'auto'" for unbalanced data set
       """
    #print 'get_trained_classifier(X=%s, y=%s, keys=%s)' % (X.shape, y.shape, len(keys))
   
    # Our current best classifier
    classifier = svm.SVC(kernel='rbf', C=0.5, gamma=0.1)
    classifier.fit(X, y, class_weight = 'auto')
    return classifier
    
"""
    y= 0: 101462
    y= 1:   6259
    y= 2:   2576
    y= 3:   1663
    y= 4:    989
    y= 5:    551
    y= 6:    340
    y= 7:    249
    y= 8:    185
    y= 9:    146
    y=10:    129
    y=11:     90
    y=12:     82
    y=13:     67
    y=14:     37
    y=15:    319
"""    
THESHOLDS = [0, 1, 2, 4, 8, 16]    

def show_dist(title, y):
    print 'show_dist "%s": num=%d, unique=%s' % (title, y.size, np.unique(y))
    for i in np.unique(y):
        print ' y=%2d: %6d' % (i, (y==i).sum())

def get_trained_classifier2(X, y, keys):
    """Return classifier trained on X and y
       X columns are typically a subset of a bigger X
       y is a numeric array
       No resampling as this is for part of a data set
       NOTE use of "class_weight = 'auto'" for unbalanced data set
       """
    print 'get_trained_classifier2(X=%s, y=%s, keys=%s)' % (X.shape, y.shape, len(keys))
    show_dist('y', y)
    classifiers = {}
    classes = {}
    last = 0
    for threshold in THESHOLDS[:-1]:
        classifiers[threshold] = get_trained_classifier(X, y > threshold, keys)
        n = (y > threshold).sum()
        classes[threshold] = n
        print ' threshold=%2d: %6d %6d' % (threshold, n, n - last)
        last += n
        
    return classifiers, classes    

def make_prediction2(classifiers, x):
    """Make numeric prediction based on cascading classifiers""" 
    for threshold in THESHOLDS[:-1]:
        if not classifiers[threshold].predict(x):
            return threshold
    return THRESHOLDS[-1]
    
class CompoundClassifier:
    """
        Classifies in multiple groups (age, sex based)
        Implements regression by classification at different levels
    """
    def __init__(self, do_regression, keys, sex_key, age_key, sex_boundary, age_boundaries):
        assert(sex_key in keys)
        assert(age_key in keys)
        self._entries = []
        self._do_regression = do_regression
        self._keys = keys
        self._sex_key = sex_key
        self._age_key = age_key
        self._sex_boundary = sex_boundary
        self._age_boundaries = age_boundaries
        
    def __repr__(self):
        def s(e): return '  sex=%s,age=%s:%s' % (e['sex'],e['age'],e['classes'])
        return 'classifer\n' + '\n'.join([s(e) for e in self._entries])
    
    def get_sex_class(self, sex):
        return 'm' if sex < self._sex_boundary else 'f'
        
    def get_age_class(self, age):
        if age < self._age_boundaries[0]:
            return AGE_LOW 
        elif age > self._age_boundaries[1]:
            return AGE_HIGH    
        else:  
            return AGE_MEDIUM

    def _add(self, classifier, classes, keys, sex_class, age_class):
        assert(all([k in self._keys for k in keys]))
        self._entries.append({'classifier':classifier, 'classes':classes, 
            'keys':keys, 'sex':sex_class, 'age':age_class})

    def train(self, X, y, keys, sex_class, age_class):
        """Train a classifier, y is a boolean array"""
        print 'train(X=%s,y=%s,keys=%s' % (X.shape, y.shape, len(keys))
        if not self._do_regression:
            self._add(get_trained_classifier(X, y, keys), keys, sex_class, age_class)
        else: 
            classifier, classes = get_trained_classifier2(X, y, keys)
            self._add(classifier, classes, keys, sex_class, age_class)
        assert(X.shape[1] == len(keys))    

    def get_classifier(self, sex, age):
        sex_class = self.get_sex_class(sex)
        age_class = self.get_age_class(age)
        for i,e in enumerate(self._entries):
            #print '--%4d: %s %s' % (i, e['sex'], e['age'])
            if e['sex'] == sex_class and e['age'] == age_class:
                return e['classifier'], e['keys'] 
        raise ValueError('No classifier for sex=%s,age=%s (sex_class=%s, age_class=%d)' % (sex, age,
            sex_class, age_class)) 
    
    def show_all(self):
        common.SUBHEADING()
        for i,e in enumerate(self._entries):
            print '%4d: %s %s : %s' % (i, e['sex'], e['age'], e['classifier'])
    
    def predict(self, X, keys):
        assert(all([k in self._keys for k in keys]))
        
        sex_index = keys.index(self._sex_key)
        age_index = keys.index(self._age_key)
    
        def predict_one(x):
            sex = x[sex_index]
            age = x[age_index]
            classifier, classifier_keys = self.get_classifier(sex, age)
            key_indexes = np.array([(k in classifier_keys) for k in self._keys])
            xc = x[key_indexes]
            if not self._do_regression:
                return classifier.predict(xc)
            else :
                return make_prediction2(classifier, xc)

        y = np.zeros(X.shape[0])
        for i in range(X.shape[0]):
            y[i] = predict_one(X[i,:])
            
        return y     
    
def run_model(X, y, keys):
    import os
    import random
    from sklearn import metrics
    from sklearn.cross_validation import StratifiedKFold
        
    DO_REGRESSION = True
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
 
    #Xr, yr = select_features.resample_equal_y(X, y, 1.0)
    #Xr, yr = normalize(Xr, yr)
    Xr, yr = X, y

    sex_vals = np.unique(Xr[:,keys.index('Sex')])
    age_vals = np.unique(Xr[:,keys.index('AgeAtFirstClaim')])
    sex_boundary = sex_vals.mean()
    age_boundaries = [0.5*(age_vals[i]+age_vals[i+1]) for i in [0,age_vals.size-2]] 
    print 'sex_vals = %s' % sex_vals
    print 'age_vals = %s' % age_vals
    print 'sex_boundary = %s' % sex_boundary
    print 'age_boundaries = %s' % age_boundaries

    def make_classifier(X_train, y_train):
        classifier = CompoundClassifier(DO_REGRESSION, keys, 'Sex', 'AgeAtFirstClaim', 
            sex_boundary, age_boundaries)
      
        for sex in ['f', 'm']:
            for age in AGES:
                show_dist('y_train', y_train)
                Xsa,ysa,ksa = getXy_by_sex_age(X_train, y_train, keys, sex, age, sex_boundary, 
                    age_boundaries)
                show_dist('ysa', ysa)    
                if DO_TOP_FEATURES:
                    # Use only the best X columns
                    assert(Xsa.shape[1] == len(ksa))
                    Xsa,ksa = filter_by_keys(Xsa, ksa, top_features[sex][age])
                    assert(Xsa.shape[1] == len(ksa))
                    
                print 'Xsa=%s,Xsa=%s,ksa=%d' % (Xsa.shape, ysa.shape, len(ksa))
                classifier.train(Xsa, ysa, ksa, sex, age)

        #classifier.show_all() 
        return classifier
        
    if False:
        def make_predictor(X_train, y_train):
            predictor = {}
            for threshold in [0, 1, 2, 4, 8]:
                classifier = make_classifier(X_train, y_train > threshold)
                predictor[threshold] = classifier
            return predictor
            
        def do_predict(predictor, X_test, keys):
            print 'do_predict %d' % X_test.shape[0]
            predictions = np.zeros(X_test.shape[0])
            for i in range(predictions.size):
                predictions[i] = 16
            for threshold in sorted(predictor.keys()):
                classifier = predictor[threshold]
                
                y = classifier.predict(X_test, keys)
                print ' predictor[%s] = %s' %(threshold, y.sum())
                for i in range(predictions.size):
                    if not y[i]:
                        predictions[i] = threshold
            return predictions

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
        
        if DO_REGRESSION:
            #predictor = make_predictor(X_train, y_train)
            #y_pred = do_predict(predictor, X_test, keys)
            classifier = make_classifier(X_train, y_train)
            y_pred = classifier.predict(X_test, keys)
            print 'classifier = %s' % (classifier)
            print 'accuracy = %f' % get_accuracy(y_pred, y_test)
        else:
            classifier = make_classifier(X_train, y_train)
            y_pred = classifier.predict(X_test, keys)
            P('Classification report for classifier %s:\n%s\n' % (classifier, 
                    metrics.classification_report(y_test, y_pred)))

        y_test_all = np.r_[y_test_all, y_test]
        y_pred_all = np.r_[y_pred_all, y_pred]    

    common.HEADING()
    if DO_REGRESSION:
        print 'Overall accuracy = %f' % get_accuracy(y_pred_all, y_test_all)
    else:    
        print 'Classification report for all %s:\n%s\n' % (
                        classifier, metrics.classification_report(y_test_all, y_pred_all))
        print 'Confusion matrix:\n%s' % metrics.confusion_matrix(y_test_all, y_pred_all)
    
    
if __name__ == '__main__':
        
    features = 'all2'
    threshold = 0
    X,y,keys = getXy_by_features_(-1, features)
    print 'unique y values = %s' % np.unique(y)
    for i in np.unique(y):
        print 'y=%2d: %6d' % (i, (y==i).sum())
    
    run_model(X, y, keys)
    
    