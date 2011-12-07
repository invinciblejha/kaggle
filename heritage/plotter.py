from __future__ import division
"""
   Plot some Heritage files

"""
import numpy as np
import matplotlib.pyplot as plt
import common

def histo(title, a_list):
    x = a_list
    hist,bins = np.histogram(x, bins=50)
    width=0.7*(bins[1]-bins[0])
    center=(bins[:-1]+bins[1:])/2
    plt.bar(center, hist, align='center', width=width)
    plt.title(title)
    plt.show()

if __name__ == '__main__':
    import sys
    import optparse

    parser = optparse.OptionParser('python ' + sys.argv[0] + ' options <file name>')
    parser.add_option('-i', '--histogram', dest='plot_histo', default=False, help='plot histogram')
  
    (options, args) =  parser.parse_args()
    
    if options.plot_histo:
        filename,column_key = options.plot_histo.split(':')
        title = filename
        vals = common.get_dict(filename, column_key, int).values()
        
        common.summarize(title, vals)
        histo(title, vals)
        
        vals1 = [i for i in vals if i != 0]
        title1 = title + ' (0 excluded)'
        common.summarize(title1, vals1)
        histo(title1, vals1)
     
    