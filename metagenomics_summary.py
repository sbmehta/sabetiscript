#!usr/bin/env python
"""Script to summarize a series of single sample metagenomics tables.
Specify a list of files below, in this script file.

The names for the files should be of the form #samplename.#classifier.#summary.#txt
For example: a001.kraken.summary.txt

The individual files should be a tab-separated table, with columns headers in the first
line of the file, including at a minimum:
taxID: an NCBI taxonomic id
taxName: the name corresponding to the taxID (leading spaces are ignored)
    reads: number of reads at this taxon or below
taxReads: number of reads specifically at this taxon 
rank: taxonomic category (Phylum, Class, Order, Family, Genus, Species)
These columns can appear in any order as long as the names exactly match those above.

The script includes preprocessing below that will MODIFY the input files to:
1) Removes empty lines or lines starting with # from the file
2) Replace the % character with the letters "pct" anywhere it appears in a column name
3) Add the harcoded list of column headers (see script below) if the file starts with numbers.
These are conveniences to deal with the Kraken output formats generated by viral-ngs;
please modify either the preprocessing section below or your files to ensure the correct format.
"""

import os
import re
from glob import glob
import fileinput
import pandas as pd


# PARAMETERS
filelist = glob("*.txt")

"""
# Clean up headers to make them consistent / Python-friendly
# (can comment out if not needed)
for summaryfile in filelist:
inheader = True
for line in fileinput.input(summaryfile, inplace=1):
if not inheader:
print(line,end="")
elif re.search(r'^[\n#]', line):  # drop empty lines & lines starting with "#"
continue
elif re.search(r'%', line):       # convert % in the column names to a more code-friendly "pct"
print(re.sub('%', 'pct', line),end="")
inheader = False   # now that we fixed the headers, just copy the rest of the file with no change
elif re.search(r'^\s*\d+', line): # if the first non-blank/non-comment line starts with a number (ignoring whitespace) ...
print("pct\treads\ttaxReads\trank\ttaxID\ttaxName\n",end="") # ... add these col names hard-coded for my Kraken files
print(line,end="")
inheader = False
"""

# Combine all files into a big table
alldata = pd.DataFrame({'pct':0, 'reads':0, 'taxReads':0, 'rank':'-', 'taxID':-1, 'taxName':'DUMMY', 'source':'-', 'classifier':'-', 'indent':-1.0}, index=[0])
for summaryfile in filelist:
    filename_parse = re.split("\.", os.path.split(summaryfile)[1])
    data = pd.read_csv(summaryfile,sep='\t',header=0,nrows=10)
    data['source'] = filename_parse[0]         # keep track of sample ...
    data['classifier'] = filename_parse[1]     #      ... and classifier
    data['indent'] = (data['taxName'].str.len() - data['taxName'].str.lstrip().str.len())/2
    data['taxName'] = data['taxName'].str.lstrip()

    Nunclassified = data[data.taxID == 0].reads.iloc[0]
    Nroot = data[data.taxID == 1].reads.iloc[0]
    Ntotal = Nunclassified + Nroot

    row = pd.DataFrame({'pct':100.0, 'reads':Ntotal, 'taxReads':0, 'rank':'-', 'taxID':-1, 'taxName':'ALL', 'source':filename_parse[0], 'classifier':filename_parse[1], 'indent':-1.0}, index=[len(alldata)])
    data.index = data.index + (len(alldata) + 1)
    alldata = alldata.append(row.append(data))
    

# Subset the parts of the table we want
#alldata = alldata[alldata.classifier.str.match(classifier)]
#alldata = alldata[['source','taxID','taxName','reads']]
