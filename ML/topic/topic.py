#!/usr/bin/env python
# -*- coding: utf-8 -*-

#####################################################################
######### Author: Kenneth Emeka Odoh                        #########
######### Purpose: Topic labeling of text data              #########
######### Description: Using  labeled LDA                   #########
#####################################################################

## TO DO
## sort out issues with data set inputing
## figure out how to update the model


from __future__ import division

import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

import string, random, numpy
from llda import LLDA
from collections import defaultdict
import os, sys, getopt, cPickle, csv, sklearn
import os.path

import copy_reg
import types
import multiprocessing

import pandas as pd

	
import hashlib


import os 
dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"

def getTweetPythonPath (dir_path):
    currentPath = dir_path.split("/")
    tweetsList = currentPath[:-2] + ["tweets"]
    tweetDir = "/".join(tweetsList)
    return tweetDir






from extra import stopwords, diff, removePunctuation
from twokenize import tokenizeRawTweetText, splitToken

#handling the pickling object
def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)


#MESSAGES = pd.read_csv(dir_path+'data/topicCollection', names=["label", "message"])

MESSAGES = pd.read_csv(dir_path+'data/topicCollection.csv')
    

class TopicDetector:
    '''
        Topic detector class
    '''
    filename = None
    labels = []
    corpus = []
    wordEmbeddings = None
    tflag = False

    def __init__( self, filename = None ):
        if not filename:
            self.filename = dir_path+'models/topic_model.pkl'
        #self.init ()


    def init (self):
        '''
        tweetDir = getTweetPythonPath (dir_path)

        sys.path.insert(0, tweetDir)
        from tweets import  TweetSimilarity
        '''

        ispresent =  os.path.exists(self.filename)
        #twt = TweetSimilarity ( )
        #self.wordEmbeddings = twt.getWholeTweetEmbeddings() # tweet.py must create the embeddings in an incremental manner
        if ispresent:
            self.loaded_dict = cPickle.load(open(self.filename)) #get the dictionary    
        else:
            #disable training here
            self.train ()

        #set the training flag
        self.tflag = ispresent 




    def train (self, alpha = 0.001, beta  = 0.001, iteration = 100, termCnt = 100):
        '''
            modify the data set to the labeled data set of choice
        '''
        seed = None
        random.seed(seed)
        numpy.random.seed(seed)

        for index, row in MESSAGES.iterrows():
            listOfLabels = row['label'].split(',')
            listOfLabels = [x.strip() for x in listOfLabels]
            sentences = str(row["message"])

            self.labels.append( listOfLabels )
            self.corpus.append( [x.lower() for x in tokenizeRawTweetText(sentences) if x not in string.punctuation and x.lower() not in stopwords ] )

        nlabelset = list(set(reduce(list.__add__, self.labels)))

        llda = LLDA( alpha, beta)
        llda.set_corpus(nlabelset, self.corpus, self.labels)

        for i in range(iteration):
            llda.inference()

        phi = llda.phi()

        output = defaultdict(list)

        for k, label in enumerate(nlabelset):
            for w in numpy.argsort(-phi[k])[:termCnt]:
                output[label].append (llda.vocas[w]) 

        self.writeModelTofile (output, self.filename)
        self.loaded_dict = output #set the dictionary    

        return output


    def label (self, text, score = 1.0/100):
        """
            input: text
            output: text, topiclist
        """

        ltext = text.lower()
        docset = set (ltext.split()) #tokens in text

        total = []

        for label, listOfTerms in self.loaded_dict.iteritems():
            topicset = set (listOfTerms) #tokens in topic set
            output = {"text": None, "label": []}
            if self.__match_ratio(topicset, docset) > score:
                output["text"] = text
                output["label"].append (label)

            #make tweet semantic search here
            '''
            try:
                if self.wordEmbeddings:
                    vscore = self.wordEmbeddings.n_similarity( diff( list( topicset ), stopwords ), diff( list(docset), stopwords )  )
                    if vscore > score:
                        output["text"] = text
                        output["label"].append (label)
            except KeyError, e:
                #ignore to prevent the program from halting
                pass
            except AttributeError, e:
                #ignore to prevent the program from halting
                pass
            '''

            if output["text"] and output["label"]:
                total.append (output)

        ntotalist = defaultdict(list) #hash with label lists
        nlist = {} #hash with text values
        
        #process the total
        for obj in total:
            hash_object = hashlib.md5(obj["text"])
            hash_str = hash_object.hexdigest()
            ntotalist[hash_str].extend (obj["label"])
            nlist[obj["text"]] = hash_str

        topicList = []
        try:
            hashVal = nlist[text]
            topicList = ntotalist[hashVal]
        except KeyError, e:
            pass
        #return {"text": text, "labels": list( set (topicList) )}
        return {"labels": list( set (topicList) )}


    def bulkLabel (self, messages): 
        lst = []
        for message in messages:
            label = self.label ( message )
            lst.append ( label )

        return lst
                           

    def __match_ratio(self,topicset, docset):
        '''
            Due to the small size of a tweet. The threshold should be set as small as possible
        '''
        commonset = docset & topicset
        return len (commonset) / len (topicset)


    def writeModelTofile (self, classifier, file_name):
        '''
            write to file
        '''
        with open(file_name, 'wb') as fout:
            cPickle.dump(classifier, fout)
        print 'model written to: ' + file_name

 

    def isTrained (self):
        """
            Output:
                True if model is trained
                False if model is not trained
        """

        ispresent =  os.path.exists(self.filename)
        #set the training flag
        self.tflag = ispresent 
        return self.tflag


       
if __name__ == "__main__": 
    tm = TopicDetector()
    #tm.init ( )
    #tm.train()
    #print tm.label ("I love dating")
    #messages = ["it is a weather in the game", "I am lovely"]
    #print tm.bulkLabel (messages)

    print "list of keywords"
    print dict (tm.train())






