# Machine Learning Pipeline

Install all the required dependencies using

Install redis
$ sudo apt-get install redis-server

Start the redis service

$ pip install -U -r requirements.txt

You can remove all the compiled files .pyc, stale files and stored object models. This is needed for clean up before pushing to github.

$ python clean.py

The MLService folder contains the periodic task for getting the data from the database and performing machine learning processing and feeding the output of the pipeline to redis.

The model is also trained in this file. check for initialization.py and content.py respectively.

The periodic task is logged in celery.logs and the entire application is saved in data.logs
 

The machine learning operation are contained in
    
    /MLService
        /ML

# ML

This contains the following
        Sentiment classifier
            labels
                4 for neutral sentiment, 
                2 for positive sentiment, 
                0 for negative sentiment
        Spam classifier
            labels
                ham for good tweet
                spam for bad tweet
        Summarizer
        Topic detection
        Tweet Similarity Detector

The service is currently a json object that is streamed at interval. Once the database connection is ready, we can query the database using the interval on the timestamp to get slice of data which will be preprocessed with the machine learning modules and labeled appropriately for consumptions in the frontend.

To start the web service inside the MLService folder
    
$ python app.py


Open up a terminal and use curl
    
$ curl -i http://127.0.0.1:8001/v1/messages

You will see the json objects in a stream.

Consume the data in a frontend using techniques such as desribed in ( https://stephennewey.com/realtime-websites-with-flask/ ).

# Datasets

The sentiment classification data is available in ML/sentiment/twitter_data. The current data is a dummy data. However, the real data can be obtained from ( https://www.dropbox.com/sh/s0ctb2cjpi9rj7a/AADAF7rp_0whlTCCtKvv0JkRa?dl=0 ).





# API for ML and MLService

This can be found in the root directory using the file.
The server application can be found in app.py.

#File Structures

    /MLServices
        app.py
        helper.py
        requirements.txt
        clean.py
        initialization.py
        Procfile
        content.py
        __init__.py
        README.md

        /scraper
            scraper.py

        /test
            test.py

        /log
            celery.logs
            data.logs

        /ML
            /ner
                __init__.py   
                ner.py 
                setup.sh 
                twokenize.py

            /sentiment
                __init__.py
                /models        
                /twitter_data
                sentiment.py  

            /spam
                __init__.py
                /data  
                /models  
                spam.py 

            /summarizer
                __init__.py  
                summarizer.py  

            /topic
                __init__.py
                /data
                /models
                llda.pyc  
                extra.py       
                llda.py       
                topic.py  
                twokenize.py

            /tweets
                __init__.py
                /models 
                tweetData.py  
                tweets.py      
                twokenize.py

            pipeline.py

#Description of the output objects and json object from the RESTful service

Version: v1

GET /v1/messages

[
{ "text": tweet, "spam": spam, "topic": [], "sentiment": sentiment, "location": [],  "person": [], "organization": [] }
]


GET /v1/similarwords

obtain list of words similar to the given word

POST /v1/similarlists

obtain list of words similar to the given words when either the positive or negative list of words or both are provided

GET /v1/similarsentences

Obtain list of tweets similar to the provided tweet.

GET /similarhashtags

obtain list of hashtags similar to the given hashtag

POST /v1/similarhashtagslists

obtain list of hashtags similar to the given hashtag when either the positive or negative list of hashtags or both are provided

#Limitations
Celery is still the best non-blocking library for periodic cron-like job in Python land.
Celery library does not work nicely with multiprocessing with scikit-learn depends on it. See ( https://github.com/celery/celery/issues/3340 ). However, I tricked it to fork demons by calling a python script from a terminal within the python code. This must force the process to fork and hence allow multiprocessing to work for the scikit learn and other machine learning libraries.


#Security issues
The pickling of object from an untrusted source such as Twitter feeds is very dangerous. However, in content.py we are pickling a json representation of the tweets in order to feed to json. I tried to load and encode json without success. Kindly take note of this known issues as an attacker may write shell commands as tweets and once our system reads it. There can be issues.
