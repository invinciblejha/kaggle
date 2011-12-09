from __future__ import division
"""
   Plot some Heritage files

"""
import common


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
        plotter.plot_histo(title, vals)
        
        vals1 = [i for i in vals if i != 0]
        title1 = title + ' (0 excluded)'
        common.summarize(title1, vals1)
        plotter.plot_histo(title1, vals1)
     
    