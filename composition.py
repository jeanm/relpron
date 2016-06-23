from nlip import Embeddings, LexicalFunctions
import numpy as np

# Returns the composed relative clauses in a dataset, given the noun embeddings
# and lexical functions for verbs and relative pronouns.
def compose(dataset, nouns, verbs_s, verbs_o, rpt_s, rpt_o, rpm_s, rpm_o):
    plf = []  # practical lexical function model
    rpt = []  # relative pronoun tensors
    rpm = []  # relative pronoun matrices
    for sbj_or_obj, target, noun1, relative_pronoun, verb, noun2 in dataset:
        # subject relative clauses
        if sbj_or_obj == "SBJ":
            plf.append(np.dot(verbs_s.word(verb), nouns.word(noun1)) +
                              np.dot(verbs_o.word(verb), nouns.word(noun2)))
            # note: tensors were matricised, so tensor contraction reduces to
            # matrix multiplication with a flattened outer product
            rpt.append(np.dot(rpt_s.word(relative_pronoun),
                              np.outer(nouns.word(noun1),
                                       np.dot(verbs_o.word(verb), nouns.word(noun2))
                                      ).flatten()))
            rpm.append(np.dot(rpm_s.word(relative_pronoun),
                              np.hstack((nouns.word(noun1), np.dot(verbs_o.word(verb), nouns.word(noun2))))))
        # object relative clauses
        else:
            plf.append(np.dot(verbs_s.word(verb), nouns.word(noun2)) +
                              np.dot(verbs_o.word(verb), nouns.word(noun1)))
            rpt.append(np.dot(rpt_o.word(relative_pronoun),
                              np.outer(nouns.word(noun1),
                                       np.dot(verbs_s.word(verb), nouns.word(noun2))
                                      ).flatten()))
            rpm.append(np.dot(rpm_o.word(relative_pronoun),
                              np.hstack((nouns.word(noun1), np.dot(verbs_s.word(verb), nouns.word(noun2))))))
    return (plf, rpt, rpm)
