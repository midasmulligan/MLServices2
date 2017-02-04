from anomaly import tSeries as ts
from anomaly import trigger as trig
from summarizer import summarizer as summ
from datastore import DataStore

import pandas as pd
import os.path
from random import randrange, sample

dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"


class AGGREGATION:
    MINUTE = 1
    HOUR = 2
    DAY = 3


class Pipeline ():
    'Common base for machine learning pipeline'
    __predFutureObj = None
    __triggerObj = None

    term = ""
    testFlag = False

    def __init__( self, term=None ):
        '''
            Constructor
        '''

        if term:
            term = term.lower()
            self.ds = DataStore ()

            #if table does not exist
            if not self.ds.table_exists( term):
                #create table
                self.ds.createTable( term )


            self.__predFutureObj = ts.PredictedFutureTriggerAlerts( term )
            self.__triggerObj = trig.TriggerAlerts( term )

            self.term = term

        else:
            self.__predFutureObj = ts.PredictedFutureTriggerAlerts(  )

            self.__triggerObj = trig.TriggerAlerts( )


    def setData ( self, ndf ):

        self.__predFutureObj.setData (ndf)
        self.__triggerObj.setData (ndf)


    def setAggregation ( self, state ):
        self.__predFutureObj.state = state


    def getAggregation ( self ):
        return self.__predFutureObj.state 


    def simulatedPredict ( self, p=1, q=1, interval = 1, h=10 ):
        '''
            list of every triggers not in use
        '''
        return self.__predFutureObj.simulatedPredict (p=p, q=q, interval=interval, h=h )



    def train(self, interval = 1):
        '''
            train the model
        '''

        timeAgg = self.getAggregation (  )
        if not self.testFlag:
        
            if timeAgg == AGGREGATION.MINUTE:

                self.__triggerObj.useMinutes (interval = interval)

            elif timeAgg == AGGREGATION.HOUR:

                self.__triggerObj.useHours (interval = interval)

            else:

                self.__triggerObj.useDays (interval = interval)

            self.testFlag = True



    def getContent (self, start, end, interval = 1, sentiment = None):
        '''
            label the text with spam, topic and sentiment information
        '''
 
        output = []

        curr = { } 


        dataDict = None

        #get df from database
        df = None

        if sentiment:
            df = self.ds.getDF( self.term, start, end, sentiment )
        else:
            df = self.ds.getDF( self.term, start, end )


        df.index = pd.to_datetime( df.timestamp, unit ='s' )

        NUMOFSENTENCES = 50


        if not df.empty:
            #ensure the dataframe is not empty

            self.setData ( df )

            timeAgg = self.getAggregation (  )

            #train the model

            self.train( interval )
        
            if timeAgg == AGGREGATION.MINUTE:

                dataDict = self.__triggerObj.useMinutes (interval = interval)

            elif timeAgg == AGGREGATION.HOUR:

                dataDict = self.__triggerObj.useHours (interval = interval)

            else:

                dataDict = self.__triggerObj.useDays (interval = interval)

            #print dataDict ['2017-02-03 01:14:00']

            #totalString = ' '.join( dataDict ['2017-02-03 01:14:00'] )

            outputDict = {}
            for key, textlists in dataDict.iteritems():
                #shuffle the list
                random_index = randrange(0,len(textlists))
                sampleList = textlists[random_index] 

                summarizedTxt = ''.join([item for item in sampleList[:NUMOFSENTENCES]])

                outputDict.update({key: summarizedTxt })

            futureSpikeTimes = self.simulatedPredict (  )


      

            sentimentDict = {'pos': 'positive', 'neg': 'negative', 'neu': 'neutral'}

            if sentiment:
                curr = { 
                    "term": self.term, 
                    "sentiment": sentimentDict[sentiment],
                    "trend": len(outputDict) > 3,
                    "summary": outputDict, 
                    "future trending spike times": futureSpikeTimes
                }

            else:
                curr = { 
                    "term": self.term, 
                    "trend": len(outputDict) > 3,
                    "summary": outputDict, 
                    "future trending spike times": futureSpikeTimes
                }

 


        output.append ( curr )

        del df #release memory


        return output


if __name__ == "__main__":  
    mlPipe = Pipeline ( "trump" )
    #mlPipe.setAggregation ( 1 )

    print mlPipe.getContent (1486083488, 1486167449 )


