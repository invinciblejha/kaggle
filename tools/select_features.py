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

import sklearn
from sklearn import datasets, neighbors, linear_model
from sklearn.metrics import confusion_matrix
from sklearn import cross_validation

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


_logistic = linear_model.LogisticRegression()
def get_cv_score(X,y):
    f_log = cross_validation.cross_val_score(_logistic, X, y, cv=3, score_func=sklearn.metrics.f1_score)
    return sum(f_log)/len(f_log)
    
def test_cv():
    digits = datasets.load_digits()
    print 'logistic cv = %.2f' % get_cv_score(digits.data, digits.target)

def list_to_str(a_list):
    return '_'.join('%04d'% f for f in sorted(a_list)) 

def str_to_list(a_str):
    return [str(f) for f in a_str.split('_')] 
    
def get_most_predictive_features(X, y, feature_set):
    print 'get_most_predictive_features: X=%s,y=%s,features=%s' % (X.shape, y.shape, feature_indices)  
    scores = {}
    print 'feature, score'
    for f in feature_set:
        indexes = str_to_list(a_str)
        Xf = X[indexes]
        scores[f] = get_cv_score(Xf, y)
        print '%5.2f %s %d' % (scores[f], indexes, len(indexes))
    return scores

    
 MAX_FEATURE_SETS = 20    
def get_most_predictive_feature_set(X, y, feature_indices):  
     
    # feature sets are MAX_FEATURE_SETS elements
    # each element is a set of n ints
    # n grows in each round
 
    def grow(feature_sets_list):
        print 'grow(%d)' % len(str_to_list(feature_sets_list[0]))
        feature_sets_list1 = []
        for i, fi in enumerate(len(feature_sets_list)):
            for j, fj in enumerate(i+1, len(feature_sets_list)):
                for k in fj:
                    feature_string = list_to_str(str_to_list(fi) + [k]) 
                    if not feature_string in feature_sets_list1:
                        feature_sets_list1.append(feature_string)
                    if len(feature_sets1) >= MAX_FEATURE_SETS:
                        return [str_to_list(f) for f in feature_sets1
                        
    feature_sets_list = [str_to_list([i]) for i in feature_indices]

    all_scores = {}
    while True:
        scores = get_most_predictive_features(X, y, feature_sets_list)
        feature_sets_list = sorted(list(scores.keys()), key=lambda k:-scores[k])
        n = len(str_to_list(feature_sets_list[0]))
        all_scores[n] = scores
        if n > len(feature_indices)/2:
            break
        feature_sets_list = grow(feature_sets_list)

if __name__ == '__main__':
    test_cv()
    