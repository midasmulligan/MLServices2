from timeSeries import TimeSeriesPrediction
import pandas as pd


class AGGREGATION:
    MINUTE = 1
    HOUR = 2
    DAY = 3


class PredictedFutureTriggerAlerts:


    def __init__ ( self, term=None ):
        from trigger import TriggerAlerts
        self.state = AGGREGATION.MINUTE

        if term:
            self.tAlertObj = TriggerAlerts(term )
        else:
            self.tAlertObj = TriggerAlerts( )


    def setData (self, ndf):
        self.tAlertObj.setData (ndf)


    def setAggregation (self, state):
        self.state = state


    def useMinutes (self, interval = 1):
        '''
            minute aggregation
        '''
        self.state = AGGREGATION.MINUTE

        dataDict = self.tAlertObj.useMinutes ( interval )
        outputDict = {}
        for key, value in dataDict.iteritems():
            outputDict.update({key: len(value)})
        return outputDict

                   
    def useHours(self, interval = 1):
        '''
            hour aggregation
        '''
        self.state = AGGREGATION.HOUR

        dataDict = self.tAlertObj.useHours ( interval )
        outputDict = {}
        for key, value in dataDict.iteritems():
            outputDict.update({key: len(value)})
        return outputDict


    def useDays(self, interval = 1):
        '''
            day aggregation
        '''
        self.state = AGGREGATION.DAY

        dataDict = self.tAlertObj.useDays ( interval )
        outputDict = {}
        for key, value in dataDict.iteritems():
            outputDict.update({key: len(value)})
        return outputDict


    def removeTrigger (self, term):
        '''
            remove triggers not in use
        '''
        return self.tAlertObj.removeTrigger (term)


    def getEveryTriggers (self):
        '''
            list of every triggers not in use
        '''
        return self.tAlertObj.getEveryTriggers ( )



    def deleteEveryTriggers (self):
        '''
            list of every triggers not in use
        '''
        return self.tAlertObj.deleteEveryTriggers ( )



    def simulatedPredict (self, p=1, q=1, interval = 1, h=10 ):
        '''
            list of every triggers not in use
        '''
        ndata = None

        if self.state == AGGREGATION.MINUTE:
            ndata = self.useMinutes ( interval = interval )

        elif self.state == AGGREGATION.HOUR:
            ndata = self.useHours( interval = interval )

        else:
            #self.state = AGGREGATION.DAY
            ndata = self.useDays( interval = interval )


        data = pd.DataFrame(
            {
                'timestamp': ndata.keys(),
                'amount': ndata.values()
            }
        )

        data.index = data['timestamp'].values

        tsData = TimeSeriesPrediction(data, p, q)
        tsData.update(data, p, q)

        predTimeSeriesData = tsData.predict (h)
        return predTimeSeriesData.index.tolist()


if __name__ == "__main__":

    file = open('data.json', 'r')
    json_str = file.read()
    df = pd.read_json(json_str)
    ndf = df [1:]
    ndf.timestamp = pd.to_datetime(ndf.timestamp, unit ='s')
    ndf = ndf.set_index('timestamp')

    tsaObj = PredictedFutureTriggerAlerts( "kenneth" )
    tsaObj.setData (ndf)

    print "========================================\n"
    print tsaObj.useMinutes (interval = 1) #training mode
    print "========================================\n"

    print tsaObj.simulatedPredict () #testing mode


