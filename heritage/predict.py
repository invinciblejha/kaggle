"""
http://scikit-learn.sourceforge.net/dev/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC

"""
#print __doc__

import math
import os
import numpy as np
from scipy import interp
import pylab as pl

import sklearn
from sklearn import svm, metrics, linear_model
from sklearn.metrics import roc_curve, auc
from sklearn.linear_model import SGDClassifier
from sklearn.cross_validation import StratifiedKFold

import common  
from common import AGES, AGE_LOW, AGE_MEDIUM, AGE_HIGH
import select_features

def plot_2d_histo_raw(x0, x1, y, label_x, label_y, x0_len, x1_len):
    """Plot a 2D histogram
       
    """
    print 'plot_2d_histo_raw(x0=%s, x1=%s, y=%s, label_x=%s, label_y=%s)' % (x0.shape, x1.shape, 
        y.shape, label_x, label_y)

    n = x0.size

    unique_0 = np.unique(x0)
    unique_1 = np.unique(x1)
    print 'unique_0=%s' % unique_0
    print 'unique_1=%s' % unique_1
    
    d0 = x0_len /(unique_0.size + 1)/2.0
    d1 = x1_len /(unique_1.size + 1)/2.0
    
    lut_0 = {}
    lut_1 = {}
    for i, u in enumerate(unique_0):
        lut_0[u] = i
    for i, u in enumerate(unique_1):
        lut_1[u] = i
    
    counts_pos = np.zeros([len(lut_0), len(lut_1)])
    counts_neg = np.zeros([len(lut_0), len(lut_1)])

    # Make histogram
    for i in range(n):
        i0 = lut_0[x0[i]]
        i1 = lut_1[x1[i]]
        if y[i]:
            counts_pos[i0,i1] += 1.0/n 
        else:    
            counts_neg[i0,i1] += 1.0/n 

    print 'counts_pos = %s' % counts_pos.sum()      
    print 'counts_neg = %s' % counts_neg.sum() 
    
    for i0, u0 in enumerate(unique_0):
        for i1, u1 in enumerate(unique_1):
            r_pos = math.sqrt(counts_pos[i0][i1])/2.0
            r_neg = math.sqrt(counts_neg[i0][i1])/2.0
            #print ix,iy,r

            if r_pos > r_neg:
                circ = pl.Circle((u0+d0,u1+d1),radius=r_pos,color='red')
                ax = pl.gca()
                ax.add_patch(circ)
                circ = pl.Circle((u0-d0,u1-d1),radius=r_neg,color='blue')
                ax = pl.gca()
                ax.add_patch(circ)
            else:    
                circ = pl.Circle((u0-d0,u1-d1),radius=r_neg,color='blue')
                ax = pl.gca()
                ax.add_patch(circ)
                circ = pl.Circle((u0+d0,u1+d1),radius=r_pos,color='red')
                ax = pl.gca()
                ax.add_patch(circ)

    pl.xlabel(label_x)
    pl.ylabel(label_y)

def plot_classification(X, y, y_pred, keys, title, clf):
    print 'plot_classification(X=%s, y=%s, y_pred=%s, keys=%s, title=%s)' % (X.shape, 
        y.shape, y_pred.shape, keys, title)
    h = .02 # step size in the mesh
    
    n_plots = len(keys)*(len(keys)-1)//2
    n_side = int(math.sqrt(float(n_plots)))

    cnt = 1
    for i0 in range(len(keys)):
        for i1 in range(i0+1, len(keys)): 
            # create a mesh to plot in
            x_min, x_max = X[:,i0].min()-1, X[:,i0].max()+1
            y_min, y_max = X[:,i1].min()-1, X[:,i1].max()+1
            xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
            
            pl.set_cmap(pl.cm.Paired)

            # Plot the decision boundary. For that, we will assign a color to each
            # point in the mesh [x_min, m_max]x[y_min, y_max].
            print 'subplot(%d, %d, cnt=%d)' % (n_side, n_side, cnt)
            pl.subplot(n_side, n_side, cnt)
            print 'xx.size=%s, xx.shape=%s, X.shape=%s' % (xx.size, xx.shape, X.shape)
            points = np.zeros([xx.size, X.shape[1]])
            points[:,i0] = xx.ravel() 
            points[:,i1] = yy.ravel()
            Z = clf.predict(points)

            # Put the result into a color plot
            Z = Z.reshape(xx.shape)
            pl.set_cmap(pl.cm.Paired)
            pl.contourf(xx, yy, Z)
            pl.axis('tight')
            
            #pl.xlabel(keys[0])
            #pl.ylabel(keys[1])

            # Plot also the training points
            #pl.scatter(X[:,0], X[:,1], c=y)
            
            plot_2d_histo_raw(X[:,i0], X[:,i1], y, keys[i0], keys[i1], x_max-x_min, y_max-y_min)

            #pl.title('%s vs %s' % (keys[i1], keys[i0]))

            pl.axis('tight')
            cnt +=1 
            if cnt > n_side ** 2:
                break
        if cnt > n_side ** 2:
            break
            
    pl.savefig(os.path.join('results', '%s.png' % title)) 
    pl.show()

def classify_old(title, X, y, keys, get_classifier):
    print 'classify(title=%s, X=%s, y=%s, keys=%s)' % (title, X.shape, y.shape, keys)

    Xr, yr = select_features.resample_equal_y(X, y, 1.0)
    print 'classify: Xr=%s, yr=%s' % (Xr.shape, yr.shape)
    n_samples = Xr.shape[0]

    if False:
        X_train, y_train = Xr[:n_samples/2,:], yr[:n_samples/2]
        X_test, y_test = Xr[n_samples/2:,:], yr[n_samples/2:]

    NUM_FOLDS = 5
    skf = StratifiedKFold(yr, NUM_FOLDS)

    verbose = False

    if verbose:
        def P(s): print s
    else:
        def P(s): pass

    n_iter_val = 500
    for power_t_val in [0.9]:
        for alpha_val in [0.1]: 
            y_test_all = np.zeros(0)
            y_pred_all = np.zeros(0)
            for i,(train, test) in enumerate(skf):
                X_train, y_train = Xr[train,:], yr[train]
                X_test, y_test = Xr[test,:], yr[test]
            
                if verbose: common.SUBHEADING()
                P('Fold %d of %d' % (i, NUM_FOLDS))
                P('classify: X_train=%s, y_train=%s' % (X_train.shape, y_train.shape))
                P('classify:  X_test=%s,  y_test=%s' % (X_test.shape, y_test.shape))

                # fit the model
                classifier = SGDClassifier(loss="hinge", alpha=alpha_val,  
                    n_iter=n_iter_val, fit_intercept=True)
           
                classifier.fit(X_train, y_train)
                y_pred = classifier.predict(X_test)

                P('Classification report for classifier %s:\n%s\n' % (classifier, 
                    metrics.classification_report(y_test, y_pred)))
                P('Confusion matrix:\n%s' % metrics.confusion_matrix(y_test, y_pred))
                
                y_test_all = np.r_[y_test_all, y_test]
                y_pred_all = np.r_[y_pred_all, y_pred]

            common.HEADING()
            print 'Classification report for all %s:\n%s\n' % (
                    classifier, metrics.classification_report(y_test_all, y_pred_all))
            print 'Confusion matrix:\n%s' % metrics.confusion_matrix(y_test_all, y_pred_all)

            # plot the line, the points, and the nearest vectors to the plane
            if False:
                fac = 1.0
                print 'Downsampling by a further factor of %f' % fac
                X_r, y_r = sklearn.utils.resample(X, y, n_samples = int(X.shape[0] * fac)) 
            y_pred = classifier.predict(Xr)
            plot_classification(Xr, yr, y_pred, keys, title, classifier)  

def classify_by_method(title, Xr, yr, keys, get_classifier, plot):
    common.HEADING()
    print 'classify_by_method: Xr=%s, yr=%s "%s"' % (Xr.shape, yr.shape, title)
    
    n_samples = Xr.shape[0]
 
    NUM_FOLDS = 2
    skf = StratifiedKFold(yr, NUM_FOLDS)

    verbose = False

    if verbose:
        def P(s): print s
    else:
        def P(s): pass
  
    y_test_all = np.zeros(0)
    y_pred_all = np.zeros(0)
    for i,(train, test) in enumerate(skf):
        X_train, y_train = Xr[train,:], yr[train]
        X_test, y_test = Xr[test,:], yr[test]
    
        if verbose: common.SUBHEADING()
        P('Fold %d of %d' % (i, NUM_FOLDS))
        P('classify: X_train=%s, y_train=%s' % (X_train.shape, y_train.shape))
        P('classify:  X_test=%s,  y_test=%s' % (X_test.shape, y_test.shape))

        # fit the model
        classifier = get_classifier()
   
        classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_test)

        P('Classification report for classifier %s:\n%s\n' % (classifier, 
            metrics.classification_report(y_test, y_pred)))
        P('Confusion matrix:\n%s' % metrics.confusion_matrix(y_test, y_pred))
        
        y_test_all = np.r_[y_test_all, y_test]
        y_pred_all = np.r_[y_pred_all, y_pred]
    
    if verbose: common.SUBHEADING()
    print 'Classification report for all %s:\n%s\n' % (
            classifier, metrics.classification_report(y_test_all, y_pred_all))
    print 'Confusion matrix:\n%s' % metrics.confusion_matrix(y_test_all, y_pred_all)

    # plot the line, the points, and the nearest vectors to the plane
    if False:
        fac = 1.0
        print 'Downsampling by a further factor of %f' % fac
        X_r, y_r = sklearn.utils.resample(X, y, n_samples = int(X.shape[0] * fac)) 
    if plot:
        y_pred = classifier.predict(Xr)
        plot_classification(Xr, yr, y_pred, keys, title, classifier)
        
def get_trained_classifier(X, y, keys):
    """Return classifier trained on X and y
       X columns are typically a subset of a bigger X
       No resampling as this is for part of a data set
       """
    print 'get_trained_classifier(X=%s, y=%s, keys=%s)' % (X.shape, y.shape, len(keys))
    
    #Xr, yr = select_features.resample_equal_y(X, y, 1.0)
    
    # Our current best classifier
    classifier = svm.SVC(kernel='rbf', C=0.5, gamma=0.1)
    classifier.fit(X, y)
    return classifier

class CompoundClassifier:
    def __init__(self, keys, sex_key, age_key, sex_boundary, age_boundaries):
        assert(sex_key in keys)
        assert(age_key in keys)
        self._entries = []
        self._keys = keys
        self._sex_key = sex_key
        self._age_key = age_key
        self._sex_boundary = sex_boundary
        self._age_boundaries = age_boundaries
        
    def get_sex_class(self, sex):
        return 'm' if sex < self._sex_boundary else 'f'
        
    def get_age_class(self, age):
        if age < self._age_boundaries[0]:
            return AGE_LOW 
        elif age > self._age_boundaries[1]:
            return AGE_HIGH    
        else:  
            return AGE_MEDIUM

    def add(self, classifier, keys, sex_class, age_class):
        assert(all([k in self._keys for k in keys]))
        self._entries.append({'classifier':classifier, 'keys':keys, 'sex':sex_class, 'age':age_class})
        
    def train(self, X, y, keys, sex_class, age_class):
        self.add(get_trained_classifier(X, y, keys), keys, sex_class, age_class)
        assert(X.shape[1] == len(keys))

    def get_classfier(self, sex, age):
        sex_class = self.get_sex_class(sex)
        age_class = self.get_age_class(age)
        for i,e in enumerate(self._entries):
            print '--%4d: %s %s' % (i, e['sex'], e['age'])
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
            classifier, classifier_keys = self.get_classfier(sex, age)
            print 'classifier:', classifier
            key_indexes = np.array([(k in classifier_keys) for k in self._keys])
            print 'key_indexes = %s' % key_indexes
            xc = x[key_indexes]
            return classifier.predict(xc)

        y = np.zeros(X.shape[0])
        for i in range(X.shape[0]):
            y[i] = predict_one(X[i,:])
            
        return y 
 
def classify(title, X, y, keys):
    print 'classify(title=%s, X=%s, y=%s, keys=%s)' % (title, X.shape, y.shape, keys)

    Xr, yr = select_features.resample_equal_y(X, y, 1.0)
       
    n_iter_val = 500
    power_t_val = 0.9
    alpha_val = 0.1 

    def get_sgd_hinge():
        return SGDClassifier(loss="hinge", alpha=alpha_val, n_iter=n_iter_val, fit_intercept=True)
 
    def get_rbf_svc():
        return svm.SVC(kernel='rbf', C=0.5, gamma=0.1)
        
    return classify_by_method(title + '_rbf', Xr, yr, keys, get_rbf_svc, True)

def compare_classifiers(title, X, y, keys):
    print 'compare_classifiers(title=%s, X=%s, y=%s, keys=%s)' % (title, X.shape, y.shape, keys)

    Xr, yr = select_features.resample_equal_y(X, y, 1.0)
   
    n_iter_val = 5000
    power_t_val = 0.9
    alpha_val = 0.1 
    CACHE_SIZE = 2000

    def get_sgd_hinge():
        return SGDClassifier(loss="hinge", alpha=alpha_val, n_iter=n_iter_val, fit_intercept=True)

    def get_svd_linear(): 
        return svm.SVC(kernel='linear')
        
    def get_svd_poly():    
        return svm.SVC(kernel='poly')

    def get_nu_linear():
        return svm.NuSVC(kernel='linear')

    def get_rbf_svc():
        return svm.SVC(kernel='rbf', C=0.5, gamma=0.1)
        
    def get_linear_svc():
        return svm.LinearSVC()
        
    def get_bayes_ridge():
        return linear_model.BayesianRidge()
        
    def get_log_reg_l1():    
        return linear_model.LogisticRegression(C=1.0, penalty='l1', tol=1e-6)
     
    def get_log_reg_l2():    
        return linear_model.LogisticRegression(C=1.0, penalty='l2', tol=1e-6)
        
    def get_lars():    
        return linear_model.LassoLars(alpha = 0.1)    
        
    def get_lasso():
        return linear_model.Lasso(alpha = 0.1)  

    def get_ridge():
        return linear_model.Ridge (alpha = 0.5)
        
    
    # get_rbf_svc works best followed by get_log_reg_l*
    classifiers = {
        'sgd_hinge': get_sgd_hinge,
        'svd_linear': get_svd_linear, 
        'svd_poly': get_svd_poly,
        'nu_linear': get_nu_linear,
        'linear_svc': get_linear_svc,
        'rbf_svc': get_rbf_svc,
        #'bayes_ridge': get_bayes_ridge, Not a classifier
        'log_reg_l1': get_log_reg_l1,
        'log_reg_l2': get_log_reg_l2,
        'lars': get_lars,
        'lasso': get_lasso,
        #'ridge': get_ridge,
        
    }

    slow = ['svd_poly']
    classifier_order = sorted(classifiers.keys(), key = lambda k: (k in slow, k))

    #print svm.SVC.__doc__
    if False:
        for gamma in [0.0, 0.1, 0.2, 0.5]:
            for C in [0.1, 0.2, 0.5, 1.0]:
                def func():
                    return svm.SVC(kernel='rbf', C=C, gamma=gamma)
                    #return svm.SVC(kernel='rbf', cache_size=CACHE_SIZE, C=C, gamma=gamma)
                name = '%s_gamma=%.2f_C=%.2f' % (title, gamma, C)
                classify_by_method(name, Xr, yr, keys, func, False)

    for name in classifier_order:
        func = classifiers[name]
        classify_by_method(title + '_' + name, Xr, yr, keys, func, False)    

def predict(X, y, keys):

    print 'predict(%s, %s)' % (X.shape, y.shape, keys)

    # Run classifier with crossvalidation and plot ROC curves
    cv = StratifiedKFold(y, k=6)
    classifier = svm.SVC(kernel='linear', probability=True)
    
    print 'got classifier'

    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)
    all_tpr = []

    for i, (train, test) in enumerate(cv):
        print '%d: about to fit' % i
        probas_ = classifier.fit(X[train], y[train]).predict_proba(X[test])
        print '%d: done fitting' % i
        
        # Compute ROC curve and area the curve
        fpr, tpr, thresholds = roc_curve(y[test], probas_[:,1])
        print '%d: got ROC' % i
        mean_tpr += interp(mean_fpr, fpr, tpr)
        mean_tpr[0] = 0.0
        roc_auc = auc(fpr, tpr)
        print '%d: got AUC' % i
        pl.plot(fpr, tpr, lw=1, label='ROC fold %d (area = %0.2f)' % (i, roc_auc))

        pl.plot([0, 1], [0, 1], '--', color=(0.6,0.6,0.6), label='Luck')

        mean_tpr /= len(cv)
        mean_tpr[-1] = 1.0
        mean_auc = auc(mean_fpr, mean_tpr)
        pl.plot(mean_fpr, mean_tpr, 'k--', label='Mean ROC (area = %0.2f)' % mean_auc, lw=2)

        pl.xlim([-0.05,1.05])
        pl.ylim([-0.05,1.05])
        pl.xlabel('False Positive Rate')
        pl.ylabel('True Positive Rate')
        pl.title('Receiver operating characteristic example')
        pl.legend(loc="lower right")
        pl.show()