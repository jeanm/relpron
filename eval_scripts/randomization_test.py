#!/usr/bin/env python

# Copyright (C) 2016 Laura Rimell <laura.rimell@cl.cam.ac.uk>
# This software is licensed under the GNU General Public License, version 3.

# Randomization test for significance on output of relpron_eval.py

import sys
import random
import re
from collections import defaultdict
import numpy as np
from math import *

file1 = sys.argv[1]
file2 = sys.argv[2]

def permute_lists(x, y):
    x_perm = [0] * len(x)
    y_perm = [0] * len(x)
    zstring = ''
    for i in range(len(x)):
        z = random.randint(0,1)
        x_perm[i] = z*x[i] + (1-z)*y[i]
        y_perm[i] = (1-z)*x[i] + z*y[i]
        zstring += str(z)
    return x_perm, y_perm, zstring

file_ids = {file1: 'A', file2: 'B'}
maps = defaultdict(lambda: defaultdict(float))   # term => file A or B => map
overallmap = defaultdict(int)  # file A or B => overallmap
for file in [file1, file2]:
    in_aps = 0
    with open(file) as infile:
        for line in infile:
            m = re.match('^MAP:\s+([\d\.]+)', line)
            if m:
                overallmap[file_ids[file]] = m.group(1)
            if in_aps:
                if re.match('$^', line):
                    break
                m = re.match('AP for term (\S+) ([\d\.]+)', line)
                maps[m.group(1)][file_ids[file]] = m.group(2)
            m = re.match('^AP over queries = terms$', line)
            if m:
                in_aps = 1

mapdiff = np.abs(float(overallmap['A']) - float(overallmap['B']))

numer = 0
denom = 0
zstrings_used = []
for iter in range(100000):
    if iter % 1000 == 0:
        print "Iteration", str(iter)
    x = np.empty(len(maps))
    y = np.empty(len(maps))
    i = 0
    for t in maps:
        x[i] = maps[t]['A']
        y[i] = maps[t]['B']
        i += 1
    x_perm, y_perm, zstring = permute_lists(x, y)
    if zstring not in zstrings_used:
        zstrings_used.append(zstring)
        if np.abs(np.mean(x_perm) - np.mean(y_perm)) > mapdiff:
            numer +=1
        denom += 1
        numer = numer * 1.0
print "mapdiff", str(mapdiff)
print numer/denom

