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

redis = StrictRedis(host='localhost', port=6379, db=0)


### These are keys from a personal account, please change them later ###
access_token = "3050139715-TjRarpLkD0omRLE8vEoE2k61BX55PPbEuYsj6ag"
access_token_secret = "S3fxhTwNckj6eawPloAOLvGMkPBQ70x1kE5B5GZiOKPI3"
consumer_key = "H8LDtkhKcVIQYsesuvAGJfZKG"
consumer_secret = "PqOup9wu87bsmHO877DLSlLVSiH3mk4KC83OJ8AO13cQJPS4lv"





class StdOutListener(StreamListener):

    def __init__(self, term, time_interval=60):
        self.interval = time_interval
        self.siesta = 0
        self.nightnight = 0
        self.start = time.time()

        self.ds = DataStore ()
        self.term = term

        #table is created
        self.ds.createTable( term )



    def on_data(self, data):

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
                self.ds.addRowToTable( self.term, tweetID, tweetText, timestamp )

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



class TweetStream:

    def __init__ ( self ):
        self.stream = {}
        self.ds = DataStore ()


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

            l = StdOutListener( term, time_interval=interval )
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)

            api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

            self.stream[ term ] = Stream(api.auth, l)
            self.stream[ term ].filter(track=[ term ], languages=['en'], async=True)


    def stopStream(self, term):
        self.stream[ term ].disconnect() #disconnect the stream and stop streaming
        del self.stream[ term ]
        print "Stop the stream\n"

        #remove table
        self.ds.removeTable( term )



if __name__ == '__main__':

    twtStreamObj = TweetStream()
    twtStreamObj.runEveryStream( )
    twtStreamObj.stopStream( "trump")


