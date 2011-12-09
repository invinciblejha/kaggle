from __future__ import division
"""
    Some graphing function
"""
import math
import numpy as np
import matplotlib.pyplot as plt

def plot_histo(title, a_list):
    hist,bins = np.histogram(a_list, bins=50)
    width=0.7*(bins[1]-bins[0])
    center=(bins[:-1]+bins[1:])/2
    plt.bar(center, hist, align='center', width=width)
    plt.title(title)
    plt.show()
  
def plot_2d_histo_raw(counts, color, label_x, label_y):
    """Plot a 2D histogram
        x_vals contains the x values
        y_vals contains the x values
        counts[x][y] is the number of counts at x,y
    """
    
    X = []
    Y = []
    for ix in  counts.keys() :
        for iy in counts[ix].keys():
            X.append(ix)
            Y.append(iy)
    plt.scatter(X, Y, s=1, lw = 0)
    
    for ix in  counts.keys() :
        for iy in counts[ix].keys():
            r = math.sqrt(counts[ix][iy])/2.0
            #print ix,iy,r
            circ = plt.Circle((ix,iy),radius=r,color=color)
            ax = plt.gca()
            ax.add_patch(circ)
                
    plt.xlabel(label_x)
    plt.ylabel(label_y)

def get_max_count(counts):
    max_count = 0.0
    for ix in  counts.keys() :
        for iy in counts[ix].keys():
            r = counts[ix][iy]
            #print 'r[%d][%d] = %f' % (ix, iy, float(r))
            if r > max_count:
                max_count = r
    return max_count
    
def plot_2d_histo(counts, color, label_x, label_y):
    max_count = get_max_count(counts)
    print 'max_count = %f' % max_count

    for ix in counts.keys() :
        for iy in counts[ix].keys():
            #print 'counts[%d][%d] %f =>' %(ix, iy, counts[ix][iy]),
            counts[ix][iy] = float(counts[ix][iy])/ max_count
            #print '%f' %(counts[ix][iy])

    max_count = get_max_count(counts)
    print 'max_count = %f' % max_count

    plot_2d_histo_raw(counts, color, label_x, label_y)
    
if __name__ == '__main__':
    
    x_vals = [] 
    y_vals = [] 
    counts = {}
    X = 10
    Y = 3
    R = math.sqrt(X**2 + Y**2)
    for ix in range(0, X):
        counts[ix] = {}
        x = ix/X
        x_vals.append(ix)
        for iy in range(0, Y):
            y = iy/X
            y_vals.append(iy)
            r = 100*(1 - math.sqrt((x-0.1)**2 + (y-0.5)**2))/2.0
            counts[ix][iy] = r
    plot_2d_histo(counts, 'green')

    
   
    