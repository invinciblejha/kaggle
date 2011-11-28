from __future__ import division
"""
    Resample lines in specified file
"""
import math
import os

def get_lines(path):
    bytes_read = 0
    with open(path, 'rt') as f:
        for lines_read, line in enumerate(f):
            bytes_read += len(line)
            yield lines_read, bytes_read, line

def resample(in_path, out_path, ratio, size):
    lines_written = 0
    with open(out_path, 'wt') as f:
        for lines_read, bytes_read, line in get_lines(in_path):
            if lines_written <= ratio * lines_read:
                f.write(line)
            if lines_read % 10000 == 0 and lines_read:
                print ' %d %d %f %d%%' % (lines_read, lines_written, 
                    lines_written/lines_read, 
                    int(math.round(bytes_read/size * 100.0)))
    
    return lines_read, lines_written    

if __name__ == '__main__':
    import sys
    import optparse

    parser = optparse.OptionParser('python ' + sys.argv[0] + ' options <in file name> <out file name')
    parser.add_option('-r', '--ratio', dest='ratio', default='1.0', help='resampling ratio')
    (options, args) = parser.parse_args()
    in_path = args[0]
    out_path = args[1]
    assert(out_path != in_path)
   
    ratio = float(options.ratio)
    size = os.path.getsize(in_path)
    num_read, num_written = resample(in_path, out_path, ratio, size)
    
    print 'num_read = %d' % num_read
    print 'num_written = %d' % num_written
    print 'ratio = %f' % (num_written/num_read)
    