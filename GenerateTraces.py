import os
import argparse
import hashlib
import calendar
import time
import sys
import re
import random
from array import array
from collections import deque
from collections import defaultdict

os.environ['PIN_ROOT'] = "/opt/pin-3.15-98253-gb56e429b1-gcc-linux"

parser = argparse.ArgumentParser("Generates traces.")

parser.add_argument("-i", help="Crashes directory.", type=str, required=True)

parser.add_argument("-o", help="Output directory.", type=str, required=True)

parser.add_argument("-b", help="Path to binary.", type=str, required=True)

args = parser.parse_args()

if args.b[0] == '/':
        args.b = args.b[1:]

for filename in os.listdir(args.i):
        f = os.path.join(args.i, filename)
        cmd = "Tracer -b 1 -c 0 -i 0 -m 0 -q 1 -o "+args.o+"/"+filename+" -- /"+args.b+" " + f
        os.system(cmd)

for filename in os.listdir(args.o):
    f = os.path.join(args.o, filename)
    cmd = "sed -i '/[B]/!d' " + f
    os.system(cmd)
    cmd = "sed -i 's/^.............//' " + f
    os.system(cmd)
    cmd = "sed -i 's/\s.*$//' " + f
    os.system(cmd)
    cmd = "sed -i '1d' " + f
    os.system(cmd)
    cmd = "uniq "+f+" > " + f +"z"
    os.system(cmd)
    cmd = "rm " + f
    os.system(cmd)
    f=f+"z"
    cmd = "cat "+f+" > " + f[:-1]
    os.system(cmd)
    cmd = "rm " + f
    os.system(cmd)
"""

adapted from https://stackoverflow.com/questions/73956255/speed-up-re-sub-on-large-strings-representing-large-files-in-python

"""
def dedup_nuts(s):
    encode = {}
    decode = []
    lines = array('L')
    for line in s.splitlines(keepends=True):
        if (code := encode.get(line)) is None:
            code = encode[line] = len(encode)
            decode.append(line)
        lines.append(code)
    del encode
    line2ix = [deque() for line in lines]
    view = memoryview(lines)
    out = []
    n = len(lines)
    i = 0
    last_maxj = -1
    while i < n:
        maxj = (n + i) // 2
        for j in range(last_maxj + 1, maxj + 1):
            line2ix[lines[j]].appendleft(j)
        last_maxj = maxj
        line = lines[i]
        js = line2ix[line]
        assert js[-1] == i, (i, n, js)
        js.pop()
        for j in js:
            #assert i < j <= maxj
            if view[i : j] == view[j : j + j - i]:
                for k in range(i + 1, j):
                    js = line2ix[lines[k]]
                    assert js[-1] == k, (i, k, js)
                    js.pop()
                i = j
                break
        else:
            out.append(line)
            i += 1
    #assert all(not d for d in line2ix)
    return "".join(map(decode.__getitem__, out))

def minimize(filename):
    with open(filename, 'r+') as file:
        string = file.read()
        string = dedup_nuts(string)
        file.seek(0)
        file.write(string)
        file.truncate()

for f in os.listdir(args.o):
    file = os.path.join(args.o, f)
    while True:
        prevSize = os.path.getsize(file)
        minimize(file)
        currSize = os.path.getsize(file)
        if prevSize == currSize:
            break

for filename in os.listdir(args.o):
    f = os.path.join(args.o, filename)
    cmd = "sed -i '/0x/!d' " + f
    os.system(cmd)

