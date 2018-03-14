import tensorflow as tf
import pandas as pd
import re
import six
from functools import reduce

# to represent categorical vs numerical features
class FeaType:
    categorical = 0
    numerical = 1

    
# the wrapper
class VowpalWabbitWrapper:

    """Loads weights from a file; NO header allowed
    Separator can be customized but file supposed to have structure:

    col 1 => name
    col 2 => hash
    col 3 => weightValue

    
    """
    def loadWeightsFromFile(self, weightsFile, sep = '\t'): 
        self.weightsTensor = tf.contrib.lookup.HashTable(
            tf.contrib.lookup.TextFileInitializer(weightsFile,
                                                  tf.string, 0, tf.float64, 2, delimiter = sep
                                                ),
                                                           default_value = 0.0)

    """
    feaDict => dictionary of features: keys are namespaces,
    values are dictionaries on {feaname : FeaType}
    
    interactionString => string, e.g. "a*b,a*b*c"; None for no interaction
    """
    def __init__(self, feaDict, interactionsString = None):
        self.feaDict = feaDict
        self.interactionsString = interactionsString

        self.weightsTensor = None
        

    def wrapModel(self):
        # make sure the weightsTensor was initialized
        assert self.weightsTensor is not None
        # dict of all tensors to be returned
        tensorDict = {}
        # instantiate the most important tensor: the response
        tensorDict["response"] = tf.get_variable("WrappedResponse",
                                                 initializer = tf.constant(0.0,
                                                                           shape=[1],dtype=tf.float64),dtype=tf.float64)
        # add the Constant from Vowpal Wabbit
        tensorDict["response"] += self.weightsTensor.lookup(tf.constant('Constant',tf.string))
        
        tensorDict["Input"] = {}
        # create input tensors
        for namespace, features in six.iteritems(self.feaDict):
            for  feaname, featype in six.iteritems(features):
                if featype is FeaType.categorical:
                    # note how use re to cleanup feature names to avoid errors
                    tensorDict["Input"].update({feaname :
                                                tf.placeholder(tf.string, [], name="Input_"+
                                                               re.sub("\W","_void_",feaname))})
                    
                if featype is FeaType.numerical:
                    tensorDict["Input"].update({feaname :
                                            tf.placeholder(tf.float64, [], name="Input_"+
                                                           re.sub("\W","_void_",feaname))})
                    
        # create parsed input: i.e. to lookup the value in the weights table
        tensorDict["ParsedInput"] = {}
        for namespace, features in six.iteritems(self.feaDict):
            for feaname, featype in six.iteritems(features):
                if featype is FeaType.categorical:
                    tensorDict["ParsedInput"].update({feaname :
                                              tf.string_join([tf.constant(namespace+'^'+feaname+'=',dtype=tf.string),tensorDict["Input"][feaname]],
                                                             name="ParsedInput_"+re.sub("\W","_void_",feaname))})
                elif featype is FeaType.numerical:
                    tensorDict["ParsedInput"].update({feaname :
                                                      tf.constant(namespace+'^'+feaname,dtype=tf.string)})
        # extract weight(s) values (multiplied by feature value for numerical features)
        tensorDict["Values"] = {}
        for namespace, features in six.iteritems(self.feaDict):
            for feaname, featype in six.iteritems(features):
                if featype is FeaType.categorical:
                    tensorDict["Values"].update({feaname : self.weightsTensor.lookup(tensorDict["ParsedInput"][feaname])})
                elif featype is FeaType.numerical:
                    tensorDict["Values"].update({feaname : tf.multiply(tensorDict["Input"][feaname],self.weightsTensor.lookup(
                        tensorDict["ParsedInput"][feaname]))})
                # add the value to the response
                tensorDict["response"] += tensorDict["Values"][feaname]
        
        # break the interactionsString
        interactionsDict = {}
        if self.interactionsString is not None:
            interactions = self.interactionsString.strip().split(',')
            for interaction in interactions:
                interactionsDict.update({interaction : interaction.split('*')})

        # create tensors representing interactions
        tensorDict["ParsedInteractions"] = {}
        tensorDict["InteractionValues"] = {}
        for interaction, namespaces in six.iteritems(interactionsDict):
            tensorDict["ParsedInteractions"][interaction] = {}
            tensorDict["InteractionValues"][interaction] = {}
            # create programmatically lists of features to interact
            feasList = []
            for namespace in namespaces:
                feasList.append([[{"namespace" : namespace,
                                   "feaname" : k,
                                   "featype": t}] for k,t in six.iteritems(self.feaDict[namespace])])
            feasToInteract = reduce(VowpalWabbitWrapper.crossProductLists,feasList)
            # for each interaction create tag & name_value
            for fealist in feasToInteract:
                tag = reduce(lambda y,z : y+'*'+z,map(lambda x: x["feaname"], fealist))
                tensorDict["ParsedInteractions"][interaction][tag] = tf.string_join(
                    list(map(lambda x: tensorDict["ParsedInput"][x["feaname"]],fealist)),'*')
                # first map categoricals to 1 & others to their value
                tensorDict["InteractionValues"][interaction][tag] = reduce(lambda x,y : tf.multiply(x,y),
                                                                           map(
                                        lambda z: tensorDict["Input"][z["feaname"]]
                                                if z["featype"] is FeaType.numerical
                                                                               else tf.constant(1.0,dtype=tf.float64),
                                                                               fealist))
                # now take the product with the coefficients
                tensorDict["InteractionValues"][interaction][tag] = tf.multiply(
                    tensorDict["InteractionValues"][interaction][tag],self.weightsTensor.lookup(
                                                                                tensorDict["ParsedInteractions"][interaction][tag]))
                # add to the response
                tensorDict["response"] += tensorDict["InteractionValues"][interaction][tag]
        
                                                                                
                                                                               
        return tensorDict

    """ Helper Method to cross product two lists 
        Individual elements of the list are assumed to be lists
    """
    @staticmethod
    def crossProductLists(l1, l2):
        outList = []
        for _l1 in l1:
            for _l2 in l2:
                outList.append(_l1 + _l2)
        return outList
            
