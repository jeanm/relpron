# Evaluation Scripts

This directory contains evaluation scripts related to the RELPRON dataset and the article: Laura Rimell, Jean Maillard, Tamara Polajnar and Stephen Clark. 2016. *RELPRON: A Relative Clause Composition Dataset for Compositional Distributional Semantics. Computational Linguistics*. Please cite as:

```
@article{Rimell16,
  title = "RELPRON: A Relative Clause Evaluation Dataset for Compositional Distributional Semantics",
  author = "Laura Rimell and Jean Maillard and Tamara Polajnar and Stephen Clark",
  year = "2016",
  journal = "Computational Linguistics",
}
```

## Scripts included

`print_relpron_similarities.py` takes an argument indicating 'dev' or 'test', a word vector file (for the terms), and a file of composed vectors (for the properties).  Outputs a list of similarities between every <term, property> pair.  This list is used as input to most of the subsequent scripts. You will have to adjust the script for the format of your own vector files.


All of the following scripts use the output of `print_relpron_similarities.py`,
except `map_avg_hn.pl` and `randomization_test.py`, which use the output of
`relpron_eval.py`.

* `relpron_eval.py` computes MAP score on the output of `print_relpron_similarities.py`.  Gives an overall MAP, and MAP for the data broken down by head noun and grammatical function. Corresponds to Tables 6, 7, and 8 in the article.
* `eval_mrr.py` computes MRR on the output of `print_relpron_similarities.py`.  Gives the MRR by head noun and overall. Corresponds to Table 11 in the article. Uses the development data.
* `top10hn.pl` computes the average proportion of the top 10 ranked properties that have the correct head noun. Corresponds to Table 9 in the article. Uses the development data.
* `map_avg_hn.pl` calculates MAP within head nouns. Only the properties with the correct head noun are ranked for each term. Corresponds to Table 10 in the article. Uses the development data, and the input should be the output of `relpron_eval.py`.
* `randomization_test.py` randomization test for significance on two files (presumed to have used different composition methods for the properties) output by `relpron_eval.py`.
