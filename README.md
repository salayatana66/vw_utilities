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
  ingest UNIX pipes (say resultin from `hive` queries) while dumping the
  results into other pipes.
  
  Example: 
  
  `chmod +x vwUniqueFeasExtractor.py`
  
  `./vwUniqueFeasExtractor.py --interactions 'a*b,a*b*c' <inputFileOrPipe > outputFileOrPipe`

* tensorflow_wrapper is a little python package to wrap a model into a tensor flow one, e.g.
  for serving a large model **without need** to explicitly encode interactions.
  Currently the weights must be human readable, in a file of the form

  ```
  Weight Name   Hash    Weight Value
  ```

  with the **header removed**.

  1. Step 1: Import the wrapper package, e.g.
  ```
  from tensorflow_wrapper.Wrapper import FeaType as fT, VowpalWabbitWrapper as WP
  ```
  1. Step 2: Create a nested dictionary of namespace, interactin and category type, e.g.
  ```
  feaDict = {"a" : { "a1" : fT.numerical, "a2" : fT.categorical},
  	  "b" : {"b1" : fT.categorical} }
	  ```
  1. Step 3: instantiate the wrapper, e.g.:
  ```
  myWrapper = WP(feaDict, interactionsString="a*b,a*a")
  ```
  1. Step4: load the weights from a file, and wrap
  ```
  myWrapper.loadWeightsFromFile("file.tsv")
  myTensors = myWrapper.wrapModel()
  ```

  Then input is available in
  ```
  myTensors["Input"]
  ```
  as a dictionary on the feature name. And the response of the model is available as
  ```
  myTensors["response"]
  ```
