from __future__ import division
"""
    Resample lines in specified file
"""
import os
import sys

def get_lines(path):
    with open(path, 'rt') as f:
        for j, line in enumerate(f):
            yield j, line
 

def resample(in_path, out_path, ratio, size):
    num_written = 0
    bytes_read = 0
    with open(out_path, 'wt') as f:
        for num_read, line in get_lines(in_path):
            if num_written < ratio * num_read:
                f.write(line)
                num_written += 1
            bytes_read += len(line)
            if num_read % 10000 == 0 and num_read:
                print ' %d %d %f %d%%' % (num_read, num_written, 
                    num_written/num_read, int(bytes_read/size * 100.0))
    
    return num_read, num_written    
            

if __name__ == '__main__':
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
    