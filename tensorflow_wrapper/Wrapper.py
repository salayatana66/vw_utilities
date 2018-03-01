import tensorflow as tf
import pandas as pd
import re

# represents a weight
class Weight:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def __str__(self):
        return self.name + " :: " + str(self.weight)

# to represent categorical vs numerical features
class FeaType:
    categorical = 0
    numerical = 1

    
# the wrapper
class VowpalWabbitWrapper:
    """
    to import weights from a csv/tsv
    """
    @staticmethod
    def importWeights(fileName, header=True, sep = '\t'):
        weightsList = []
        with open(fileName,'rt') as wf:
            headIdx = 0
            for line in wf:
                if ((not header) or (headIdx > 0) ):
                    _name, _, _weight = line.strip().split('\t')
                    weightsList.append(Weight(_name,float(_weight)))
                else:
                    headIdx += 1
                    
        return weightsList

    """
    feaDict => dictionary of features: keys are namespaces,
    values are dictionaries on {feaname : FeaType}
    
    weightsList => list of weights

    interactionString => string, e.g. "a*b,a*b*c"
    """
    def __init__(self, feaDict, weightsList, interactionsString = None):
        self.feaDict = feaDict
        self.interactionsString = interactionsString

        self.weightsTensor = tf.contrib.lookup.HashTable(
            tf.contrib.lookup.KeyValueTensorInitializer([w.name for w in weightsList],
                                                [w.weight for w in weightsList],
                                                            key_dtype=tf.string,
                                                        value_dtype=tf.float64),
                                                           default_value = 0.0)


    def wrapModel(self):
        # dict of all tensors to be returned
        tensorDict = {}

        tensorDict["Input"] = {}
        # create input tensors
        for namespace, features in self.feaDict.iteritems():
            for  feaname, featype in features.iteritems():
                if featype is FeaType.categorical:
                    # note how use re to cleanup feature names to avoid errors
                    tensorDict["Input"].update({feaname :
                                                tf.placeholder(tf.string, [], name="Input_"+
                                                               re.sub("\W","_void_",feaname))})
                    
                if featype is FeaType.numerical:
                    tensorDict["Input"].update({feaname :
                                            tf.placeholder(tf.float64, [], name="Input_"+
                                                           re.sub("\W","_void_",feaname))})

        return tensorDict
