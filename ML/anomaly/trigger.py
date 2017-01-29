from anomaly import probabilisticEWMA
from aggreg import TimeAggregation
import pandas as pd


class TriggerAlerts:


    def __init__ ( self, term=None ):

        if term:
            self.pbObj = probabilisticEWMA(term )
        else:
            self.pbObj = probabilisticEWMA( )

        self.tAggObj = TimeAggregation()


    def setData (self, ndf):
        self.tAggObj.setdata (ndf)

        
    def useMinutes (self, interval = 1):
        '''
            return: timestamps and tweets in each timestamp
        '''
        series, tweetlist = self.tAggObj.aggregInMinutes( interval )

        currentTimestamp = series.index
        currentData = series.values

        anomlist =  self.pbObj.predict ( currentData )

        ntweetList = [tweetlist[x] for x in anomlist]

        ntimeStampList = [str(currentTimestamp[x]) for x in anomlist]

        dictionary = dict(zip(ntimeStampList, ntweetList))

        return  dictionary

                   
    def useHours(self, interval = 1):
        '''
            return: timestamps and tweets in each timestamp
        '''
        series, tweetlist = self.tAggObj.aggregInHours( interval )

        currentTimestamp = series.index
        currentData = series.values

        anomlist =  self.pbObj.predict ( currentData )

        ntweetList = [tweetlist[x] for x in anomlist]

        ntimeStampList = [str(currentTimestamp[x]) for x in anomlist]

        dictionary = dict(zip(ntimeStampList, ntweetList))

        return  dictionary


    def useDays(self, interval = 1):
        '''
            return: timestamps and tweets in each timestamp
        '''
        series, tweetlist = self.tAggObj.aggregInDays( interval )

        currentTimestamp = series.index
        currentData = series.values

        anomlist =  self.pbObj.predict ( currentData )


        ntweetList = [tweetlist[x] for x in anomlist]

        ntimeStampList = [str(currentTimestamp[x]) for x in anomlist]

        dictionary = dict(zip(ntimeStampList, ntweetList))
        return  dictionary


    def removeTrigger (self, term):
        '''
            remove triggers not in use
        '''
        return self.pbObj.removeTermToList (term)


    def getEveryTriggers (self):
        '''
            list of every triggers not in use
        '''
        return self.pbObj.getEveryTerms ( )


    def deleteEveryTriggers (self):
        '''
            list of every triggers not in use
        '''
        return self.pbObj.deleteEveryTerms ( )




if __name__ == "__main__":
    file = open('data.json', 'r')
    json_str = file.read()
    df = pd.read_json(json_str)
    ndf = df [1:]
    ndf.timestamp = pd.to_datetime(ndf.timestamp, unit ='s')
    ndf = ndf.set_index('timestamp')

    #tAggObj = TriggerAlerts("kenneth")
    tAggObj = TriggerAlerts("trump")
    #training mode
    tAggObj.setData (ndf)
    nobj =  tAggObj.useMinutes( interval = 5)
    #testing mode
    tAggObj.setData (ndf)
    nobj =  tAggObj.useMinutes( interval = 5 )

    print "Testing mode"
    print nobj

    tAggObj = TriggerAlerts( )
    print tAggObj.getEveryTriggers (  )
    tAggObj.removeTrigger ("kenneth")
    #tAggObj.deleteEveryTriggers (  )
    print tAggObj.getEveryTriggers (  )


