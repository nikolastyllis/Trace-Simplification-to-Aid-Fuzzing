import os
import hashlib
import sys
import numpy

arr = []

for filename in os.listdir(sys.argv[1]):
    f = os.path.join(sys.argv[1], filename)
    arr.append(os.path.getsize(f))
    
elements = numpy.array(arr)

mean = numpy.mean(elements, axis=0)
sd = numpy.std(elements, axis=0)

final_list = [x for x in arr if (x > mean - 2 * sd)]
final_list = [x for x in final_list if (x < mean + 2 * sd)]

for filename in os.listdir(sys.argv[1]):
    f = os.path.join(sys.argv[1], filename)
    if os.path.getsize(f) in final_list:
        continue
    else:
        os.remove(f)
