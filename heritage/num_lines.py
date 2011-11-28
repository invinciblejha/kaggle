from __future__ import division
"""
    Return the number of lines in a text file
"""
import os
import sys

def get_num_lines(path):
    with open(path, 'rt') as f:
        for j, _ in enumerate(f):
            pass
    return j   

def to_mb(size):
    return size / 1024.0 / 1024.0
    
def get_size(size):
    return '%d = %.1fm' % (size, to_mb(size))

if __name__ == '__main__':
    import optparse

    parser = optparse.OptionParser('python ' + sys.argv[0] + ' <file name>]')
    (options, args) = parser.parse_args()
    path = args[0]
   
    size = os.path.getsize(path)
    num_lines = get_num_lines(path)
    
    print 'num lines = %s' % get_size(num_lines)
    print 'size = %s' % get_size(size)
    print 'average line size = %s' % get_size(int(size/num_lines))