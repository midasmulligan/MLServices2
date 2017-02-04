import json
import time
import re
import sys
import math
import pickle
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datastore import DataStore



from redis import StrictRedis


import random



redis = StrictRedis(host='localhost', port=6379, db=0)


### These are keys from a personal account, please change them later ###
access_token = "3050139715-TjRarpLkD0omRLE8vEoE2k61BX55PPbEuYsj6ag"
access_token_secret = "S3fxhTwNckj6eawPloAOLvGMkPBQ70x1kE5B5GZiOKPI3"
consumer_key = "H8LDtkhKcVIQYsesuvAGJfZKG"
consumer_secret = "PqOup9wu87bsmHO877DLSlLVSiH3mk4KC83OJ8AO13cQJPS4lv"





class StdOutListener(StreamListener):

    def __init__(self,  time_interval=60):
        self.interval = time_interval
        self.siesta = 0
        self.nightnight = 0
        self.start = time.time()

        self.ds = DataStore ()




    def best_find( self, string, text ):
        if text in string:
            return True
        return False


    def getlist ( self ):
        '''
            list of terms
        '''
        key = "listOfTerms"
        read_list = redis.get(key)
        mylist = []
        if read_list:
            existList = pickle.loads(read_list)
            mylist.extend ( existList )
        return mylist


    def getlabel( self, string ):
        output = []
        listOfTerms = self.getlist ( )
        string = string.lower( )
        curString = ""
        for term in listOfTerms:
            if self.best_find(  string, term ):
                output.append(term)

        return output
                



    def on_data(self, data):
    #def on_status(self, data):

        if (time.time() - self.start) < self.interval:
            try:
                data = json.loads(data)

                tweetText = processTweet( data['text'] )
                tweetTimestamp_ms = int (data['timestamp_ms'])
                tweetRetweetCount = data['retweet_count']
                tweetAuthorID = data['user']['id']
                tweetAuthorFollowerCount = data['user']['followers_count']
                tweetID = int (data['id'])

                timestamp = round ( tweetTimestamp_ms / 1000 )

                #add element to table
                #randomly create sentiments
                sentimentList = ['pos', 'neg', 'neu']
                sentiment = random.choice(sentimentList)

                termlist = self.getlabel( tweetText )


                for term in termlist:
                    #table is created
                    if not self.ds.table_exists( term):
                        #create table
                        self.ds.createTable( term )

                    #add row to table
                    self.ds.addRowToTable( term, tweetID, tweetText, timestamp, sentiment )

            except:
                pass


        return True



    def on_error(self, status_code):
        print 'Error:', str(status_code)
 
        if status_code == 420:
            sleepy = 60 * math.pow(2, self.siesta)
            print "A reconnection attempt will occur in " + \
            str(sleepy/60) + " minutes."
            time.sleep(sleepy)
            self.siesta += 1
        else:
            sleepy = 5 * math.pow(2, self.nightnight)
            print "A reconnection attempt will occur in " + \
            str(sleepy) + " seconds."
            time.sleep(sleepy)
            self.nightnight += 1
        return True



def processTweet(tweet):

    # Remove special characters
    tweet = tweet.encode('ascii', 'ignore')
    # Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet)
    # Convert @username to AT_USER
    tweet = re.sub('@[^\s]+','AT_USER',tweet)
    # Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    # Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    # Trim
    tweet = tweet.strip('\'"')

    return tweet



class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



class TweetStream:
    __metaclass__ = Singleton
    def __init__ ( self ):
        self.ds = DataStore ()
        self.stream = None



    def getlist ( self ):
        '''
            list of terms
        '''
        key = "listOfTerms"
        read_list = redis.get(key)
        mylist = []
        if read_list:
            existList = pickle.loads(read_list)
            mylist.extend ( existList )
        return mylist



    def runEveryStream( self ):
        '''
            begin every terms
        '''
        
        interval = 10*60 # time interval in seconds
  
        listOfTerms = self.getlist ( )

        for term in listOfTerms:
 
            #if table does not exist
            if not self.ds.table_exists( term):
                #create table
                self.ds.createTable( term )


        l = StdOutListener( time_interval=interval )
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


        self.stream = Stream(api.auth, l)
        self.stream.filter(track=listOfTerms, languages=['en'], async=True, stall_warnings=True)
            



    def stopandRemoveStream(self, term):

        from anomaly import trigger as trig
        tAggObj = trig.TriggerAlerts( )

        listOfTerms = self.getlist ( )

        #remove from redis
        if term in listOfTerms :
            tAggObj.removeTrigger ( term )

        if self.stream:
            self.stream.disconnect() #disconnect the stream and stop streaming
            print "Stop the stream\n"


        #remove table 
        if self.ds.table_exists( term ):
            self.ds.removeTable( term )        
        

    def stopEveryStream(self):
        if self.stream:
            self.stream.disconnect() #disconnect the stream and stop streaming





if __name__ == '__main__':

    twtStreamObj = TweetStream()
    #twtStreamObj.runEveryStream( )
    twtStreamObj.stopandRemoveStream( "trump")
    twtStreamObj.stopandRemoveStream( "clinton")
    twtStreamObj.stopandRemoveStream( "brexit")
    print twtStreamObj.getlist (  )


