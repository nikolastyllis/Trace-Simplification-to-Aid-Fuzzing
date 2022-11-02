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

parser = argparse.ArgumentParser("Creates a minimized corpus.")

parser.add_argument("-i", help="Corpus directory.", type=str, required=True)

parser.add_argument("-o", help="New corpus directory", type=str, required=True)

parser.add_argument("-b", help="Path to binary", type=str, required=True)

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

def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash=hashlib.sha1):
    hashobj = hash()
    file_object = open(filename, 'rb')

    if first_chunk_only:
        hashobj.update(file_object.read(1024))
    else:
        for chunk in chunk_reader(file_object):
            hashobj.update(chunk)
    hashed = hashobj.digest()

    file_object.close()
    return hashed


"""

this code is not my own it was adapted from https://stackoverflow.com/questions/748675/finding-duplicate-files-and-removing-them

"""


def check_for_duplicates(paths, hash=hashlib.sha1):
    hashes_by_size = defaultdict(list)  # dict of size_in_bytes: [full_path_to_file1, full_path_to_file2, ]
    hashes_on_1k = defaultdict(list)  # dict of (hash1k, size_in_bytes): [full_path_to_file1, full_path_to_file2, ]
    hashes_full = {}   # dict of full_file_hash: full_path_to_file_string

    array = os.listdir(paths)
    random.shuffle(array)
    for filename in array:
                f = os.path.join(paths, filename)
                try:
                    # if the target is a symlink (soft one), this will 
                    # dereference it - change the value to the actual target file
                    file_size = os.path.getsize(f)
                    hashes_by_size[file_size].append(f)
                except (OSError,):
                    # not accessible (permissions, etc) - pass on
                    continue

    # For all files with the same file size, get their hash on the 1st 1024 bytes only
    for size_in_bytes, files in hashes_by_size.items():
        if len(files) < 2:
            continue    # this file size is unique, no need to spend CPU cycles on it

        for filename in files:
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
                # the key is the hash on the first 1024 bytes plus the size - to
                # avoid collisions on equal hashes in the first part of the file
                # credits to @Futal for the optimization
                hashes_on_1k[(small_hash, size_in_bytes)].append(filename)
            except (OSError,):
                # the file access might've changed till the exec point got here 
                continue

    # For all files with the hash on the 1st 1024 bytes, get their hash on the full file - collisions will be duplicates
    for __, files_list in hashes_on_1k.items():
        if len(files_list) < 2:
            continue    # this hash of fist 1k file bytes is unique, no need to spend cpy cycles on it

        for filename in files_list:
            try: 
                full_hash = get_hash(filename, first_chunk_only=False)
                duplicate = hashes_full.get(full_hash)
                if duplicate:
                    os.remove(filename)
               	else:
                    hashes_full[full_hash] = filename
            except (OSError,):
                # the file access might've changed till the exec point got here 
                continue
                
check_for_duplicates(args.o)

minCorpusArray = os.listdir(args.o)

for f in os.listdir(args.o):
    file = os.path.join(args.o, f)
    os.remove(file)
    
for f in os.listdir(args.i):
    if f in minCorpusArray:
    	file = os.path.join(args.i, f)
    	cmd = "cp " + file + " " + args.o
    	os.system(cmd)
