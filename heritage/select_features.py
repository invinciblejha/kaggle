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

    !@#$ Try using http://pyevolve.sourceforge.net/getstarted.html#first-example instead of grow()    
"""
print __doc__

import numpy as np
import sklearn
from sklearn import datasets, neighbors, linear_model
from sklearn.metrics import confusion_matrix
from sklearn import cross_validation
from pyevolve import G1DBinaryString
from pyevolve import G1DList
from pyevolve import GSimpleGA
from pyevolve import G1DList
from pyevolve import Selectors
from pyevolve import Consts
from pyevolve import Crossovers
import common 
import ga

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
def get_cv_score(X, y):
    #print 'get_cv_score: X=%s,y=%s' % (X.shape, y.shape) 
    f_log = cross_validation.cross_val_score(_logistic, X, y, cv=3) #, score_func=sklearn.metrics.f1_score)
    return sum(f_log)/len(f_log)
    
def test_cv():
    digits = datasets.load_digits()
    print 'logistic cv = %.2f' % get_cv_score(digits.data, digits.target)

def list_to_str(a_list):
    #print 'list_to_str(%s)' % a_list
    return '_'.join('%04d'% f for f in sorted(a_list)) 

def str_to_list(a_str):
    a_list = [int(f) for f in a_str.split('_')] 
    #print 'str_to_list(%s) => %s' % (a_str, a_list)
    return a_list
    
def get_most_predictive_features(X, y, feature_sets_list):
    #print 'get_most_predictive_features: X=%s,y=%s,features=%s' % (X.shape, y.shape, feature_sets_list)  
    scores = {}
    print 'score, feature'
    best_score = 0.0
    best_indexes = None
    for f in feature_sets_list:
        #print '>>%s' % f
        indexes = str_to_list(f)
        Xf = X[:,indexes]
        scores[f] = get_cv_score(Xf, y)
        print '%7.3f %s %d' % (scores[f], indexes, len(indexes))
        if scores[f] >= best_score:
            best_score = scores[f]
            best_indexes = indexes
    print '%7.3f %s <= best' % (best_score, best_indexes)        
    return scores

MAX_FEATURE_SETS = 240  
    
def grow(feature_sets_list):
    #print 'grow(%d) %s' % (len(str_to_list(feature_sets_list[0])), feature_sets_list)
    feature_sets_list1 = []
    for i, fi in enumerate(feature_sets_list):
        for j, fj in enumerate(feature_sets_list[i+1:]):
            for k in str_to_list(fj):
                indexes = str_to_list(fi) + [k]
                if len(set(indexes)) != len(indexes):
                    continue
                
                feature_string = list_to_str(indexes) 
                if not feature_string in feature_sets_list1:
                    feature_sets_list1.append(feature_string)
                if len(feature_sets_list1) >= MAX_FEATURE_SETS:
                    return feature_sets_list1  
    return feature_sets_list1  
    
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
    
    print 'X0 ', X0.shape
    print 'y0 ', y0.shape
    print 'X1 ', X1.shape
    print 'y1 ', y1.shape
    
    # Downsample y[i]==0 on rows
    X0r, y0r = sklearn.utils.resample(X0, y0, n_samples=X1.shape[0])  
    
    print 'X0r', X0r.shape
    print 'y0r', y0r.shape
    
    Xr = np.r_[X0r, X1]
    yr = np.r_[y0r, y1]
    
    print 'Xr ', Xr.shape
    print 'yr ', yr.shape
    
    print 'Downsampling by a further factor of %f' % fac
    Xr, yr = sklearn.utils.resample(Xr, yr, n_samples = int(Xr.shape[0] *fac))  
    print 'Xr ', Xr.shape
    print 'yr ', yr.shape
    
    return Xr, yr

_BINARY_GENOME = True    
def get_best_features(X, y):

    num_features = X.shape[1]
    
    def eval_func(chromosome):
        indexes = [chromosome[i] for i in range(len(chromosome))]
        Xf = X[:,indexes]
        score = get_cv_score(Xf, y)
        #print '  eval %.4f %3d %s' % (score, len(indexes), indexes)
        return score
    
    allowed_values = range(num_features)
    all_results = {}
    for n in range(2, num_features):
        genome_len = n
        results = ga.run_ga(eval_func, genome_len, allowed_values)
        # results are sorted best to worst so this gets best results
        # !@#$ Keep all results and use these to seed n+1 round
        all_results[n] = results[0] 
    
    if False:
        def eval_func_binary(chromosome):
            indexes = sorted([i for i in range(num_features) if chromosome[i]])
            Xf = X[:,indexes]
            score = get_cv_score(Xf, y)
            #print '  eval %.4f %3d %s' % (score, len(indexes), indexes)
            return score
            
        def eval_func_list(chromosome):
            indexes = [chromosome[i] for i in range(len(chromosome))]
            Xf = X[:,indexes]
            score = get_cv_score(Xf, y)
            #print '  eval %.4f %3d %s' % (score, len(indexes), indexes)
            return score

        results = {}    
        for n in range(2, 3):
        #for n in range(2, num_features):
            common.SUBHEADING()
            print 'n=%d' % n
            
            if _BINARY_GENOME:
                genome = G1DBinaryString.G1DBinaryString(num_features)
                genome.evaluator.set(eval_func_binary)
                genome.crossover.set(Crossovers.G1DBinaryStringXUniform)
            else:
                genome = G1DList.G1DList(n)
                genome.setParams(rangemin=0, rangemax=num_features-1)
                genome.evaluator.set(eval_func_list)
                genome.crossover.set(Crossovers.G1DListCrossoverUniform)

            ga = GSimpleGA.GSimpleGA(genome)
            ga.selector.set(Selectors.GRouletteWheel)
            ga.setGenerations(500)
            #ga.terminationCriteria.set(GSimpleGA.ConvergenceCriteria)
            ga.setMinimax(Consts.minimaxType["maximize"])
     
            #ga.setPopulationSize(100)
            ga.setMutationRate(0.02)
            ga.setCrossoverRate(1.0)

            ga.evolve(freq_stats=10)

            best = ga.bestIndividual()
            #print best
            print "Best individual score: %.3f" % best.getRawScore()
            print "Best list: %s" % sorted(best.genomeList)
            results[n] = {'score': best.getRawScore(), 'list': sorted(best.genomeList)}
            for j in sorted(results.keys()):
                print '%6d: %.3f %s' % (j, results[j]['score'], results[j]['list'])
        
        common.SUBHEADING()    
        for j in sorted(results.keys()):
            print '%6d: %.3f %s' % (j, results[j]['score'], results[j]['list'])
        return results

def get_most_predictive_feature_set(X, y, feature_indices):  
    
    # feature sets are MAX_FEATURE_SETS elements
    # each element is a set of n ints
    # n grows in each round

    y_vals = np.unique(y)
    for v in y_vals:
        print 'y=%d: %5d vals = %.3f of population' % (v, sum(y == v), sum(y == v)/y.shape[0])
    print 'all: %5d vals = %.3f of population' % (y.shape[0], 1.0)    
    common.SUBHEADING()
    X,y = resample_equal_y(X, y, 0.1)
    
    return get_best_features(X, y)
  
    if False:
        feature_sets_list = [list_to_str([i]) for i in feature_indices]

        all_scores = {}
        while True:
            common.SUBHEADING()
            scores = get_most_predictive_features(X, y, feature_sets_list)
            feature_sets_list = sorted(list(scores.keys()), key=lambda k:-scores[k])
            n = len(str_to_list(feature_sets_list[0]))
            all_scores[n] = scores
                    
            print 'num, score'
            for k in sorted(all_scores.keys()):
                print '%5d: %7.3f' % (k, max(all_scores[k].values()))
                
            if n >= len(feature_indices)-2:
                break
            feature_sets_list = grow(feature_sets_list)
            


if __name__ == '__main__':
    test_cv()
    