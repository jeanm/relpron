import time
import logging
from collections import defaultdict, Counter
import numpy as np
from nlip import Embeddings, LexicalFunctions
from nlip.utils import hms, si, Timer
from nlip import floatX
import h5py
from numpy.linalg import pinv

logging.basicConfig(level=logging.ERROR, format="[%(funcName)s] %(message)s")
logger = logging.getLogger(__name__)

# Learns lexical function matrices, e.g. adjective matrices, given word and
# compound vectors. `weight` is a lambda to calculate the weight of a training
# example from its corpus count.
def learn_matrices(words, compounds, weight=(lambda c: np.log(c)),
                   min_count=2, parameter=80, report_freq=20):

    # build LexicalFunctions object
    lfs_counter = Counter((a for a,_ in compounds.index2name))
    lfs_index2name = [a for a,_ in lfs_counter.most_common()]
    vocabsize = len(lfs_index2name)
    dim = words.shape[1]
    arr = np.zeros((vocabsize, dim, dim), dtype=floatX)
    eye = np.eye(dim)
    lfs = LexicalFunctions(arr, lfs_index2name)
    logger.info("initialised a %s x %s x %s matrix embedding tensor",
                si(vocabsize), si(dim), si(dim))

    t = Timer(interval=report_freq)
    # build a list of training examples for each modifier
    t.tic()
    phrase_examples = defaultdict(list)
    for i, z in enumerate(zip(compounds.index2name, compounds.index2count)):
        if z[1] >= min_count:
            phrase_examples[z[0][0]].append((words.name2index[z[0][1]], i, z[1]))
    logger.info("Examples built in "+t.toc(hms=True))

    # solve AX = B for each modifier
    t.tic()
    for ex_num, ex in enumerate(phrase_examples.items()):
        lf_name, examples = ex
        if len(examples) < 1:
            continue
        B = np.zeros((len(examples), dim))
        A = np.zeros((len(examples),dim))
        for i, z in enumerate(examples):
            noun_index, phrase_index, count = z
            w = weight(z[2])
            A[i] = w * words[z[0]]
            B[i] = w * compounds[z[1]]
        tmp1 = pinv(np.dot(A.T, A) + parameter * eye)
        tmp2 = np.dot(A.T, B)
        lfs.A[lfs.name2index[lf_name]] = np.dot(tmp1, tmp2).T
        if t.ready():
            t.toc()
            logger.info("%.2f%% matrices (%s)" %
                (100 * ex_num / vocabsize, si(ex_num+1)))
    logger.info("learned %s matrices in %s" % (si(vocabsize),
       t.toc(hms=True)))
    return lfs

# Learns relative clause tensors. The input parameter `which` can be set to
# "orc" for object relative clauses or "src" for subject relative clauses;
# `weight` is a lambda to compute training example weights from corpus counts;
# `min_count` is the count threshold; `parameter` a regularisation weight.
def learn_rc_tensors(words, modifiers, compounds,
                   weight=(lambda c: np.log(c)), which="orc",
                   min_count=2, parameter=80.0, report_freq=20):
    logger.info("regularisation parameter: %s", str(parameter))
    if which == "orc":
        arg1 = 3
        arg2 = 2
        logger.info("learning object relative pronouns")
    else:
        arg1 = 2
        arg2 = 3
        logger.info("learning subject relative pronouns")
    # build LexicalFunctions object
    lfs_counter = Counter((m for _,m,*_ in compounds.index2name))
    lfs_index2name = [m for m,_ in lfs_counter.most_common()]
    vocabsize = len(lfs_index2name)
    dim = words.shape[1]
    arr = np.zeros((vocabsize, dim, dim*dim), dtype=floatX)
    eye = np.eye(dim*dim)
    lfs = LexicalFunctions(arr, lfs_index2name)
    logger.info("initialised a %s x %s x %s tensor embedding tensor",
                si(vocabsize), si(dim), si(dim*dim))

    t = Timer(interval=report_freq)
    # build a list of training examples for each modifier
    t.tic()
    phrase_examples = defaultdict(list)
    for i, z in enumerate(zip(compounds.index2name, compounds.index2count)):
        if z[1] >= min_count and z[0][arg1] in modifiers.name2index:
            phrase_examples[z[0][1]].append((words.name2index[z[0][0]],
                                             modifiers.name2index[z[0][arg1]],
                                             words.name2index[z[0][arg2]],
                                             i, z[1]))
    logger.info("Examples built in "+t.toc(hms=True))

    # solve AX = B for each modifier
    t.tic()
    for ex_num, ex in enumerate(phrase_examples.items()):
        lf_name, examples = ex
        if len(examples) < 1:
            continue
        B = np.zeros((len(examples), dim))
        A = np.zeros((len(examples), dim * dim))
        for i,z in enumerate(examples):
            noun1_index, modifier_index, noun2_index, phrase_index, count = z
            w = weight(count)
            A[i] = w * np.outer(words[noun1_index], np.dot(modifiers[modifier_index],
                                words[noun2_index])).flatten()
            B[i] = w * compounds[phrase_index]
        tmp1 = pinv(np.dot(A.T, A) + parameter*eye)
        tmp2 = np.dot(A.T, B)
        lfs.A[lfs.name2index[lf_name]] = np.dot(tmp1, tmp2).T
        if t.ready():
            t.toc()
            logger.info("%.2f%% matrices (%s, %s)" %
                (100 * (ex_num+1) / vocabsize, si(ex_num+1), t.toc(hms=True)))
    logger.info("learned %s tensors in %s" % (si(vocabsize),
       t.toc(hms=True)))
    return lfs

# Learns relative clause matrices. The input parameter `which` can be set to
# "orc" for object relative clauses or "src" for subject relative clauses;
# `weight` is a lambda to compute training example weights from corpus counts;
# `min_count` is the count threshold; `parameter` a regularisation weight.
def learn_rc_matrices(words, modifiers, compounds,
                   weight=(lambda c: np.log(c)), which="orc",
                   min_count=2, parameter=80.0, report_freq=20):
    logger.info("regularisation parameter: %s", str(parameter))
    if which == "orc":
        arg1 = 3
        arg2 = 2
        logger.info("learning object relative pronouns")
    else:
        arg1 = 2
        arg2 = 3
        logger.info("learning subject relative pronouns")
    # build LexicalFunctions object
    lfs_counter = Counter((m for _,m,*_ in compounds.index2name))
    lfs_index2name = [m for m,_ in lfs_counter.most_common()]
    vocabsize = len(lfs_index2name)
    dim = words.shape[1]
    arr = np.zeros((vocabsize, dim, 2*dim), dtype=floatX)
    eye = np.eye(2*dim)
    lfs = LexicalFunctions(arr, lfs_index2name)
    logger.info("initialised a %s x %s x %s tensor embedding tensor",
                si(vocabsize), si(dim), si(2*dim))

    t = Timer(interval=report_freq)
    # build a list of training examples for each modifier
    t.tic()
    phrase_examples = defaultdict(list)
    for i, z in enumerate(zip(compounds.index2name, compounds.index2count)):
        if z[1] >= min_count and z[0][arg1] in modifiers.name2index:
            phrase_examples[z[0][1]].append((words.name2index[z[0][0]],
                                             modifiers.name2index[z[0][arg1]],
                                             words.name2index[z[0][arg2]],
                                             i, z[1]))
    logger.info("Examples built in "+t.toc(hms=True))

    # solve AX = B for each modifier
    t.tic()
    for ex_num, ex in enumerate(phrase_examples.items()):
        lf_name, examples = ex
        if len(examples) < 1:
            continue
        B = np.zeros((len(examples), dim))
        A = np.zeros((len(examples), 2 * dim))
        for i,z in enumerate(examples):
            noun1_index, modifier_index, noun2_index, phrase_index, count = z
            w = weight(count)
            A[i] = w * np.hstack((words[noun1_index], np.dot(modifiers[modifier_index],
                                words[noun2_index])))
            B[i] = w * compounds[phrase_index]
        tmp1 = pinv(np.dot(A.T, A) + parameter*eye)
        tmp2 = np.dot(A.T, B)
        lfs.A[lfs.name2index[lf_name]] = np.dot(tmp1, tmp2).T
        if t.ready():
            t.toc()
            logger.info("%.2f%% matrices (%s, %s)" %
                (100 * (ex_num+1) / vocabsize, si(ex_num+1), t.toc(hms=True)))
    logger.info("learned %s tensors in %s" % (si(vocabsize),
       t.toc(hms=True)))
    return lfs
