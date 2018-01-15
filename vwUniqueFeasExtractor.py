#!/usr/bin/env python
# This version works with Python 2.7

# (c) Andrea Schioppa -- ahisamuddatiirena@gmail.com -- 2018-01-02
# This software may be distributed under the same terms as vowpal-wabbit

import re
import sys
import argparse

################################
# parsing input
# interactions should de in the form r*r,u*c,u*f,r*u*f:
# namespace1*namespace2*...namespaceK,....
################################
parser = argparse.ArgumentParser(description='VW unique features extractor')
parser.add_argument('--interactions', dest = 'interactions', default='',type=str, nargs='?')
args = parser.parse_args()

################################
# global variables
################################
# feaDict holds the namespaces and distinct features
feaDict = {}
# interactDict holds the interactions
interDict={}
# add to interDict the interactions passed as arguments
interactions = args.interactions.strip().split(',')

################################
# interaction parser
# initializes interDict
################################
def interaction_parser():
    for _inter in interactions:
        inter_components = _inter.split('*')
        # skip when there is only one namespace in the interaction
        if len(inter_components) == 1:
            break
        interDict[_inter]={}
        interDict[_inter]['components'] = inter_components
        interDict[_inter]['values'] = {}
        # add the namespaces of the interactions to the feaDict
        for _namespace in inter_components:
            if _namespace not in feaDict:
                feaDict[_namespace] = {}

################################
# Regular expressions
################################
# to Lookup the name space
nameSpaceRegEx = re.compile('\A(\S+)\s')
# to Lookup the features
feaRegEx = re.compile('\s+(\S+)')
# to decide whether a feature is numerical
numericalRegEx = re.compile('(\S+):')

################################
# Ingest features from a VW line
################################
def wv_parse_line(line):
    # dictionary of features in the current line
    lineFeaDict = {}
    pieces = line.split('|')
    # the first piece is a label + possible weight & examples identifiers
    for piece in pieces[1:]:
        # find namespace
        nameSpaceMatch = nameSpaceRegEx.findall(piece)
        nameSpace = nameSpaceMatch[0]
        # find features
        feaMatch = feaRegEx.findall(piece)
        # add namespace
        if nameSpace not in lineFeaDict.keys():
            lineFeaDict[nameSpaceMatch[0]] = {}
            # if the feature is numerical change the name
            # add the feature name to feed into the lineFeaDict
            for fea in feaMatch:
                numericalMatch = numericalRegEx.findall(fea)
                if len(numericalMatch) > 0:
                    fea = numericalMatch[0]
                # add features to dict
                lineFeaDict[nameSpaceMatch[0]][fea] = 1
    return lineFeaDict

################################
# create interactions from a vw Line
################################
def create_interactions(lineFeaDict):
    lineInterDict = {}
    for _interaction in interDict.keys():
        feaBuffer = []
        for i,_namespace in enumerate(interDict[_interaction]['components']):
            if i == 0:
                feaBuffer = lineFeaDict.get(_namespace,{}).keys()
            else:
                feaBuffer = [_feaSx+str('*')+_feaRx for _feaSx in feaBuffer
                             for _feaRx in
                             lineFeaDict.get(_namespace,{}).keys()]
        lineInterDict[_interaction] = feaBuffer
    return lineInterDict
                

################################
# update feaDict with lineFeaDict
# returns true if an update happened
################################
def update_feaDict(lineFeaDict):
    updated = False
    for nameSpace in lineFeaDict.keys():
        if nameSpace not in feaDict:
            feaDict[nameSpace] = {}
            updated = True
        for fea in lineFeaDict[nameSpace].keys():
            if fea not in feaDict[nameSpace]:
                feaDict[nameSpace][fea]=1
                updated=True
    return updated

################################
# update interDict with lineInterDict
# returns true if an update happened
################################
def update_interDict(lineInterDict):
    updated = False
    for _interaction in lineInterDict.keys():
        for fea in lineInterDict[_interaction]:
            if fea not in interDict[_interaction]['values']:
                interDict[_interaction]['values'][fea] = 1
                updated = True
    return updated
                

################################
# Script execution
################################
interaction_parser()

with sys.stdin as inputFile, sys.stdout as outputFile:
    line = 'nonNull'
    while line != '':
        line = inputFile.readline().strip()
        # extract features from line & create interaction
        lineFeaDict = wv_parse_line(line)
        lineInterDict = create_interactions(lineFeaDict)
        # update the dictionaries
        updated1 = update_feaDict(lineFeaDict)
        updated2 = update_interDict(lineInterDict)
        if updated1 or updated2:
            outputFile.write(line+'\n')
            outputFile.flush()


