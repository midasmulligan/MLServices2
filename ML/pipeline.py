from anomaly import tSeries as ts
from anomaly import trigger as trig
from summarizer import summarizer as summ


import pandas as pd
import os.path

dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"


class AGGREGATION:
    MINUTE = 1
    HOUR = 2
    DAY = 3


class Pipeline ():
    'Common base for machine learning pipeline'
    __predFutureObj = None

    term = ""

    def __init__( self, term=None ):
        '''
            Constructor
        '''

        if term:
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



    def getContent (self, start, end, interval = 1):
        '''
            label the text with spam, topic and sentiment information
        '''
        from datastore import DataStore

        ds = DataStore ()

        output = []
        dataDict = None

        #get df from database

        df = ds.getDF( self.term, start, end )

        self.setData ( df )

        timeAgg = self.getAggregation (  )
    
        if timeAgg == AGGREGATION.MINUTE:

            dataDict = self.__triggerObj.useMinutes (interval = interval)

        elif timeAgg == AGGREGATION.HOUR:

            dataDict = self.__triggerObj.useHours (interval = interval)

        else:

            dataDict = self.__triggerObj.useDays (interval = interval)

        outputDict = {}
        for key, textlists in dataDict.iteritems():
            txtlist = [item for sublist in textlists for item in sublist]
            totalString = ' '.join( txtlist )
            summarizedTxt = summ.summarizeTweet(totalString)
            outputDict.update({key: summarizedTxt })


        futureSpikeTimes = self.simulatedPredict (  )

        curr = { 
            "topic": self.term, 
            "trend": len(outputDict) > 3,
            "summary": outputDict, 
            "future trending spike times": futureSpikeTimes
        }
        output.append ( curr )


        return output


if __name__ == "__main__":  
    mlPipe = Pipeline ()
    mlPipe.setAggregation ( state )


