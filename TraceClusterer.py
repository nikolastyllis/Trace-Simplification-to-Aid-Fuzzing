import argparse
import os
import mmap
from itertools import chain
import numpy as np
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics import calinski_harabasz_score
from collections import defaultdict
from sklearn.cluster import SpectralClustering
import pickle
from datetime import datetime
import json
import networkx as nx

def readDir(input_dir):
    trace_arrays = []
    for filename in os.listdir(input_dir):
        f = os.path.join(input_dir, filename)
        trace_arrays.append(readFile(f))

    return trace_arrays

def createKey(input_dir):
    key = {}
    i = 0
    for filename in os.listdir(input_dir):
        f = os.path.join(input_dir, filename)
        key[i]=f
        i=i+1

    return key

def remove_dups(x):
    return list(dict.fromkeys(x))

def readFile(filename):
    content_array = []
    print("- " + filename + " found!")
    with open(filename, mode="r+b") as f:
        mmap_obj = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        for line in iter(mmap_obj.readline, b""):
            line = str(line)
            line = line[2:]
            line = line[:10]
            content_array.append(int(line, 0))

    return content_array

parser = argparse.ArgumentParser("Clusters a list of program traces with k-means clustering. (Prints to stdout)")
    
parser.add_argument("-i", help="Traces directory.", type=str, required=True)

parser.add_argument("-m", help="Maximum number of clusters.", type=str, required=True)

args = parser.parse_args()

print(" >>> Parsing files...")

trace_arrays = readDir(args.i)
set_of_blocks = list(chain.from_iterable(trace_arrays))
set_of_blocks = remove_dups(set_of_blocks)
trace_dict = createKey(args.i)
num_of_traces = len(trace_dict)

n = len(set_of_blocks)

print(" >>> Making adjacency matrices... (this can take a little while)")
#Construct adjacency matrices
adjacency_array = np.zeros((num_of_traces,n,n), int)

for trace in range(len(trace_arrays)):
    print("- " + str(trace + 1) + " out of " + str(len(trace_arrays)) + " adjacency matrices generated!")
    for block in range(len(trace_arrays[trace])-1):
        relative_block_1 = set_of_blocks.index(trace_arrays[trace][block])
        relative_block_2 = set_of_blocks.index(trace_arrays[trace][block+1])
        adjacency_array[trace][relative_block_1][relative_block_2] = adjacency_array[trace][relative_block_1][relative_block_2] + 1

adjacency_array = adjacency_array.reshape(num_of_traces,n*n)

print(" >>> Calculating optimal number of clusters... (this can take a little while)")
scores = []
offset = 2
maxScore = 0
optimalK = 0

for k in range(offset, int(args.m) + 1):
    print("- Testing silhouette score for " + str(k) + " clusters!")
    kmeans = KMeans(n_clusters=k, random_state=0).fit(adjacency_array)
    score = silhouette_score(adjacency_array,kmeans.labels_,metric='euclidean')
    print(score)

    if score > maxScore:
        maxScore = score
        optimalK = k
print(" >>> Generating clusters... (this can take a little while)")

kmeans = KMeans(n_clusters=optimalK, random_state=0).fit(adjacency_array)

results_dict = {}

for k in range(optimalK):
    cluster = []
    for i in range(len(kmeans.labels_)):
        if(kmeans.labels_[i] == k):
            cluster.append(trace_dict[i])

    results_dict[k] = cluster

json_data = json.dumps(results_dict, indent=4)

print(json_data)
