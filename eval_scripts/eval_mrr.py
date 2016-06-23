#!/usr/bin/env python

# Copyright (C) 2016 Laura Rimell <laura.rimell@cl.cam.ac.uk>
# This software is licensed under the GNU General Public License, version 3.

# Computes MRR on RELPRON for the output of print_relpron_similarities.py.

import sys
import re
from collections import defaultdict, OrderedDict

testfile = sys.argv[1]

goldfile = 'devset'

gold = defaultdict(str)   # prop => term
hns = defaultdict(str)   # prop => hn
ranks = defaultdict(lambda: defaultdict(int))   # hn => prop => rank
defin_to_term = defaultdict(lambda: defaultdict(float))   # defin => term => cosine


for line in open(goldfile):
    m = re.match('^([OS])BJ (\S+)_N: (\S+)_N that (\S+)_[VN] (\S+)_[VN]\s*$', line)
    term = m.group(2)
    hn = m.group(3)
    defin = m.group(1) + " " + m.group(3) + "_N that " + m.group(4) + " " + m.group(5)
    gold[defin] = term
    hns[defin] = hn

term = ""
for line in open(testfile):
    m = re.match('TERM: (\S+)', line)
    if m:
        term = m.group(1)
    m = re.match('[01] ([\d\.]+) ([SO] .+)', line)
    if m:
        defin_to_term[m.group(2)][term] = float(m.group(1))

for d in defin_to_term:
#    print "DEFIN:", d
    orderedTerms = OrderedDict(sorted(defin_to_term[d].items(), key = lambda x: x[1], reverse=True))
    rank = 1
    for x in orderedTerms:
#        print x, orderedTerms[x]
        if x == gold[d]:
            ranks[hns[d]][d] = rank
#            print "**** Setting rank =", rank
            break
        rank += 1
#    print
#    print



properties_per_hn = defaultdict(int)  # hn => number properties
mean_rr_by_hn = defaultdict(float)    # hn => running total of reciprocal rank
tot_properties = 0
overall_mean_rr = 0
for hn in ranks:
    for prop in ranks[hn]:
        properties_per_hn[hn] += 1
        tot_properties += 1
        mean_rr_by_hn[hn] += 1.0 / ranks[hn][prop]
        overall_mean_rr += 1.0 / ranks[hn][prop]
for hn in ranks:
    mean_rr_by_hn[hn] = mean_rr_by_hn[hn] / properties_per_hn[hn]
overall_mean_rr = overall_mean_rr / tot_properties

for hn in ranks:
    print hn, mean_rr_by_hn[hn]
print "Overall", overall_mean_rr
