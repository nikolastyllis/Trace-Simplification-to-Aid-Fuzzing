# Trace-Simplification-to-Aid-Fuzzing

This repository contains five python scripts. All scripts need to be run as root :/ ...

1. GenerateTraces.py will generate simplified traces for all crashing inputs in the directory pointed to by -i and output the traces to the directory pointed to by -o. It also requires the path to the binary pointed to by -b.

2. MinimizeCorpus.py will minimize a corpus directory pointed to by -i and output the new corpus to the directory pointed to by -o. It also requires the path to the binary pointed to by -b.

3. TraceClusterer.py will cluster traces in a directory pointed to by -i and output to stdout. It also takes -m the possible number of clusters to probe for optimal k.

4. Deduplicate.py will deduplicate files in the path passed to it.

5. RemoveOutliers.py will remove outlier traces by file size in the path passed to it.

It requires the tool 'Tracer' to be set up. This can be found at https://github.com/SideChannelMarvels/Tracer.

It was evaluated on the MAGMA state-of-the-art ground truth fuzzing benchmark. This can be found at https://github.com/HexHive/magma.
