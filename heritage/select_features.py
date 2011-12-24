from __future__ import division
"""
    Given X,y find the features in X that best predict y where prediction is measured
    with k-fold cross-validation
    
    Chooose a classifier C e.g. logistic regression
    
    Rank individual features by prediction
    
    For n = 1 .. num features -1
        Using best n-tuples of features
        Create n+1 tuples
        Find best using GA
  
"""
print __doc__

import numpy as np
import sklearn
from sklearn import datasets, neighbors, linear_model
from sklearn.metrics import confusion_matrix
from sklearn import cross_validation
import common 
import ga as GAX

if False:
    digits = datasets.load_digits()
    X_digits = digits.data
    y_digits = digits.target

    n_samples = len(X_digits)

    X_train = X_digits[:.9*n_samples]
    y_train = y_digits[:.9*n_samples]
    X_test = X_digits[.9*n_samples:]
    y_test = y_digits[.9*n_samples:]

    knn = neighbors.NeighborsClassifier()
    logistic = linear_model.LogisticRegression()

    fit_knn = knn.fit(X_train, y_train)
    fit_log = logistic.fit(X_train, y_train)

    y_knn = fit_knn.predict(X_test)
    cm_knn = confusion_matrix(y_test, y_knn)

    y_log = fit_log.predict(X_test)
    cm_log = confusion_matrix(y_test, y_log)

    print 'KNN score:', fit_knn.score(X_test, y_test)
    print cm_knn
    print 'LogisticRegression score:', fit_log.score(X_test, y_test)
    print cm_log

    scores_log = cross_validation.cross_val_score(logistic, digits.data, digits.target, cv=5)
    f_log = cross_validation.cross_val_score(logistic, digits.data, digits.target, cv=5, 
        score_func=sklearn.metrics.f1_score)
    print 'logistic cv  ', scores_log, sum(scores_log)/len(scores_log)
    print 'logistic cv f', f_log, sum(f_log)/len(f_log)

_classifier = linear_model.LogisticRegression()
#_classifier = neighbors.NeighborsClassifier(n_neighbors=5)

def get_cv_score(X, y):
    #print 'get_cv_score: X=%s,y=%s' % (X.shape, y.shape) 
    f_log = cross_validation.cross_val_score(_classifier, X, y, cv=3) #, score_func=sklearn.metrics.f1_score)
    return sum(f_log)/len(f_log)

def test_cv():
    digits = datasets.load_digits()
    print 'logistic cv = %.2f' % get_cv_score(digits.data, digits.target)

def resample_equal_y(X, y, fac):
    """Resample X,y to have equal values of y[i]==0 and y[i]==1 over samples X[i],y[i]
        The following code assumes
            y has only 2 values, 0 and 1
            y[i]==1 is less common than y[i]==0
            there are many y[i]==1 samples (=> downsampling is ok)
    """
       
    X0 = X[y==0,:]
    X1 = X[y==1,:]
    y0 = y[y==0]
    y1 = y[y==1]
    
    if False:
        print 'X0 ', X0.shape
        print 'y0 ', y0.shape
        print 'X1 ', X1.shape
        print 'y1 ', y1.shape
    
    # Downsample y[i]==0 on rows
    X0r, y0r = sklearn.utils.resample(X0, y0, n_samples=X1.shape[0])  
    
    if False:
        print 'X0r', X0r.shape
        print 'y0r', y0r.shape
    
    Xr = np.r_[X0r, X1]
    yr = np.r_[y0r, y1]
    
    if False:
        print 'Xr ', Xr.shape
        print 'yr ', yr.shape
        
    if fac != 1.0:
        print 'Downsampling by a further factor of %f' % fac
        Xr, yr = sklearn.utils.resample(Xr, yr, n_samples = int(Xr.shape[0] * fac))  
        print 'Xr ', Xr.shape
        print 'yr ', yr.shape

    return Xr, yr
 
def get_best_features(X, y, keys):

    num_features = X.shape[1]
    
    def eval_func(chromosome):
        indexes = [chromosome[i] for i in range(len(chromosome))]
        Xf = X[:,indexes]
        score = get_cv_score(Xf, y)
        #print '  eval %.4f %3d %s' % (score, len(indexes), indexes)
        return score
    
    allowed_values = range(num_features)
    all_results = {}
    best_genomes = None
    for n in range(1, num_features+1):
    #for n in range(1, 14):
    #for n in range(1, 3):
        genome_len = n
        results = GAX.run_ga(eval_func, genome_len, allowed_values, best_genomes)
        results = GAX.run_ga2(eval_func, genome_len, allowed_values, 5, best_genomes)
        # results are sorted best to worst so this gets best results
        all_results[n] = results[0] 
        last_score = 0.0
        for k in sorted(all_results.keys()):
            score = all_results[k]['score']
            genome = all_results[k]['genome']
            decoded = [keys[g] for g in genome]
            print '%6d: %.3f (%.4f) %s %s' % (k, score, score-last_score, genome, decoded)
            last_score = score
        best_genomes = [r['genome'] for r in results]    
    return all_results    
 
def get_most_predictive_feature_set(X, y, keys):  
    common.SUBHEADING()
    print 'get_most_predictive_feature_set(X=%s, y=%s, keys=%s)' % (X.shape, y.shape, keys)
    X,y = resample_equal_y(X, y, 1.0)
    return get_best_features(X, y, keys)

if __name__ == '__main__':
    test_cv()
    