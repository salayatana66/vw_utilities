# Utilities for Machine Learning in Vowpal Wabbit

In this repo I plan to add utilities to work with
[Vowpal Wabbit](https://github.com/JohnLangford/vowpal_wabbit/).

* `vwUniqueFeasExtractor.py` is a program that summarizes features and
  interactions in the training set to produce a new test set on which
  **hash inversion** is faster. The reason to write this is that
  `utl/vw-varinfo` in
  [Vowpal Wabbit](https://github.com/JohnLangford/vowpal_wabbit/) does
  not ingest UNIX pipes. Working as a DS in a production environment
  where hash inversion is required on large datasets I have used it to
  ingest UNIX pipes (say result from `hive` queries) and dumped the
  results into other pipes.
  
  Example: 
  
  `chmod +x vwUniqueFeasExtractor.py`
  
  `./vwUniqueFeasExtractor.py --interactions 'a*b,a*b*c' < \
  inputFileOrPipe > outputFileOrPipe`
