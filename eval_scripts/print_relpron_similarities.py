#!/usr/bin/env python

# Copyright (C) 2016 Laura Rimell <laura.rimell@cl.cam.ac.uk>
# This software is licensed under the GNU General Public License, version 3.

# Takes a file of word vectors and a file of composed RELPRON property vectors.
# Output consists of similarities between every (word, property) pair.
# Similarities are ordered from highest to lowest for each word.
# The output format is as expected by relpron_eval.py.

import numpy as np
import pickle
from collections import defaultdict
from collections import OrderedDict
import sys
import re
import os
import scipy.spatial.distance as distance

dev_or_test = sys.argv[1]
word_vec_file = sys.argv[2]
composed_vec_file = sys.argv[3]

words = pickle.load(open(word_vec_file, 'rb'))
rctest = pickle.load(open(composed_vec_file, 'rb'))

if dev_or_test == 'dev':
    goldfile = 'devset'
else:
    goldfile = 'testset'

def cos(a, b):
    try:
        len(a) == len(b)
    except(ValueError):
        print ("cos: a and b must have same length")
    numer = 0
    denoma = 0
    denomb = 0
    for i in range(len(a)):
    	ai = a[i]
    	bi = b[i]
    	numer += ai*bi
    	denoma += ai*ai
    	denomb += bi*bi
    if denoma == 0 and denomb == 0:
        return 0
    return numer / (np.sqrt(denoma)*np.sqrt(denomb))

terms = defaultdict(int)    # term => count
defs = []   # definitions
gold = defaultdict(lambda: defaultdict(bool))   # term => definition => true
sims = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))  # composition_type => term => definition => similarity score

for line in open(goldfile):
    m = re.match('^([OS]BJ) (\S+)_N: (\S+)_N that (\S+)_[VN] (\S+)_[VN]\s*$', line)
    defin = m.group(1) + " " + m.group(2) + ": " + m.group(3) + " that " + m.group(4) + " " + m.group(5)

    if defin == 'SBJ friction: phenomenon that prevent slipping': 
        defin = 'SBJ friction: phenomenon that prevent slip'

    defs.append(defin)
    terms[m.group(2)] += 1
    gold[m.group(2)][defin] = True

for defin in defs:
    m = re.match('^\s*[SO] (\S+)_N that (\S+)_[VN] (\S+)_[VN]\s*$', defin)

for t in terms:
    for d in defs:
        if d not in rctest:
            print("skipping", d)
            continue

        sims['composed'][t][d] = cos(words[t], rctest[d])

# print similarities
for comptype in sims:
    for t in terms:
        print("TERM: " + t)
        orderedDefins = OrderedDict(sorted(sims[comptype][t].items(), key = lambda x: x[1], reverse=True))
        for d in orderedDefins:
            relevant = 0
            if d in gold[t]:
                relevant = 1

            m = re.match('^([OS])BJ \S+: (\S+) that (.*)$', d)
            defstring = m.group(1) + " " + m.group(2) + "_N that " + m.group(3)

            print(str(relevant) + " " + str(orderedDefins[d]) + " " + defstring)
        print("END TERM")

