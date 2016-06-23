#!/usr/bin/env python

# Copyright (C) 2016 Laura Rimell <laura.rimell@cl.cam.ac.uk>
# This software is licensed under the GNU General Public License, version 3.

# Computes MAP on RELPRON for the output of print_relpron_similarities.py.
# Assumes all properties are ranked by similarity.

from __future__ import division
import sys
import re
import numpy as np
from collections import defaultdict

infile = open(sys.argv[1])

aps = defaultdict(float)   # term => ap
aps_by_gf = defaultdict(lambda: defaultdict(float))  # S|O => term => ap
aps_by_hn = defaultdict(lambda: defaultdict(float))  # headnoun => term => ap

apnums = defaultdict(int)   # condition (term, S|O, headnoun) => AP numerator, used during calculation to keep track of different APs
ranks = defaultdict(int)    # condition (term, S|O, headnoun) => rank, used during calculation, only incremented if example matches
rels = defaultdict(int)     # condition (term, S|O, headnoun) => number of relevant examples, used during calculation, only incremented if example matches

for line in infile:

    m = re.match('TERM: (.*)', line)
    if m:
        term = m.group(1)
        apnums.clear()
        ranks.clear()
        rels.clear()
        
    m = re.match('([01])\s+[\d\.\-]+\s+([SO])\s+(\S+)_N\s+.*', line)
    if m:
        isrel = int(m.group(1))    # 1 = relevant, 0 = not relevant
        gf = m.group(2)            # grammatical function of relative clause
        hn = m.group(3)            # head noun
        
        ranks['term'] += 1
        ranks[gf] += 1
        ranks[hn] += 1

        if isrel:
            rels['term'] += 1
            rels[gf] += 1
            rels[hn] += 1
            apnums['term'] += (rels['term'] / ranks['term'])
            apnums[gf] += (rels[gf] / ranks[gf])
            apnums[hn] += (rels[hn] / ranks[hn])

    m = re.match('END TERM', line)
    if m:
        if rels['term'] == 0:
            aps[term] = 0
        else:
            aps[term] = apnums['term'] / rels['term']
        for gf in ['S', 'O']:
            if rels[gf] == 0:
                aps_by_gf[gf][term] = 0
            else:
                aps_by_gf[gf][term] = apnums[gf] / rels[gf]
        for x in apnums:
            if x == 'term' or x == 'S' or x == 'O':    # apnums contains conditions including 'term', S|O, and headnouns
                continue
            if rels[x] == 0:
                aps_by_hn[x][term] = 0
            else:
                aps_by_hn[x][term] = apnums[x] / rels[x]

map = np.mean(aps.values())
print "MAP: ", str(map)

print
print


print "AP over queries = terms"
        
for t in aps:
    print "AP for term", t, str(aps[t])


print
print


print "AP over queries = terms, breakdown by Grammatical Function"

for gf in aps_by_gf:
    zero_terms = []   # list of terms with no relevant properties in this gf
    print "GRAMMATICAL FUNCTION", gf
    for t in aps_by_gf[gf]:
        print "AP wrt GF", gf, t, str(aps_by_gf[gf][t])
        if aps_by_gf[gf][t] == 0:
            zero_terms.append(t)

    # before calculating map, remove zero entries since these represent cases where there are no relevant 
    # properties for this term for this gf
    for t in zero_terms:
        del aps_by_gf[gf][t]

    map = np.mean(aps_by_gf[gf].values())

    print
    print
    print "MAP for: ", gf, ":", str(map)
    print
    print


print "AP over queries = terms, breakdown by Head Noun"

for hn in aps_by_hn:
    print "HEAD NOUN", hn
    for t in aps_by_hn[hn]:
        print t, str(aps_by_hn[hn][t])
    map = np.mean(aps_by_hn[hn].values())
    print
    print "MAP for: ", hn, ":", str(map)
    print

