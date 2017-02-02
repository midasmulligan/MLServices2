
# API DOCUMENTATION


The RESTful API is version 1.

Aggregation takes the form of a number with either of {M, H, D}

| Symbols | Description |
| --- | --- |
| M | minutes |
| H | hours |
| D | days |

This is how it is used "1M" (1 minute interval time aggregation), "2M" (2 minute interval time aggregation), "1H" (1 hour interval time aggregation), "2H" (2 hour interval time aggregation), "1D" (1 day interval time aggregation), "2D" (2 days interval time aggregation). This is related to the frequency of the time series.


Sentiment can take any of the following words which is either "pos", "neg", "neu".

| Sentiment | Description |
| --- | --- |
| "pos" | positive |
| "neg" | negative |
| "neu" | neutral |



# Full Description of API with use cases

### Create a new user


Parameter: username (string), password (string)

Method: /v1/api/users

Usage:
$ curl -i -X POST -H "Content-Type: application/json" -d '{"username":"miguel","password":"python"}' http://127.0.0.1:8001/v1/api/users

Output:
{
  "username": "miguel"
}


## Streaming Mode


### Create an alert using only term


Default aggregation is 1 minutes

Parameters: term (string)

method: /v1/alerts/`<term>`

Usage:
```
$ curl -u miguel:python -i -X GET http://127.0.0.1:8001/v1/alerts/trump
```

Where the username name is miguel and password is python. The alert is trump which is every data related to identifying the anomalies in the data stream.

Output:

{ 
    "term": trump, 
    "trend": True | False,
    "summary": {time : summarized text }, 
    "future trending spike times": []
}

The summary is the spikes and a summarization of the tweets at the spikes.

### Create an alert using term and aggregation

Parameters: term (string), aggregation (string)

method: /v1/alerts/`<term>/<aggregation>`

Usage:
```
$ curl -u miguel:python -i -X GET http://127.0.0.1:8001/v1/alerts/trump/1H
```

Where the username name is miguel and password is python. The alert is trump which is every data related to identifying the anomalies in the data stream by setting the time aggregation (1 hour time aggregation).

Output:
{ 
    "term": trump, 
    "trend": True | False,
    "summary": {time : summarized text }, 
    "future trending spike times": []
}

The summary is the spikes and a summarization of the tweets at the spikes.

## Batch Mode

### Create an alert using term, time extent (start and end date strings) and aggregation


The start and end string takes the form of "day/month/year"

Parameters: term (string), start (string), end (string), aggregation (string)

method: /v1/alerts

Usage:

start parameter must be provided.

Example 1: provide both start and end values

```
$ curl -u miguel:python -i -X POST -H "Content-Type: application/json" -d '{"start":"01/12/2011", "end":"01/12/2015", "term":"clinton", "aggregation": "5H", "sentiment": "pos" }' http://127.0.0.1:8001/v1/alerts
```

Where the username name is miguel and password is python. The alert is clinton with positive sentiment that is related to identifying the anomalies in the data stream by setting the 5 hour time aggregation between 01/12/2011 and 01/12/2015.

Example 2: provide only start values as the current date is the current timestamp

```
$ curl -u miguel:python -i -X POST -H "Content-Type: application/json" -d '{"start":"01/12/2011", "term":"clinton", "aggregation": "5H", "sentiment": "neu"}' http://127.0.0.1:8001/v1/alerts
```

Example 3: provide only start values as the current date is the current timestamp

```
$ curl -u miguel:python -i -X POST -H "Content-Type: application/json" -d '{"start":"01/12/2011", "term":"clinton", "aggregation": "5H"}' http://127.0.0.1:8001/v1/alerts
```

Where the username name is miguel and password is python. The alert is clinton with neutral sentiment that is related to identifying the anomalies in the data stream by setting the 5 hour time aggregation between 01/12/2011 and current date.

Output:


Output:
{ 
    "term": clinton, 
    "sentiment": positive | negative | neutral,
    "trend": True | False,
    "summary": {time : summarized text }, 
    "future trending spike times": []
}

OR

if sentiment is missing.

{ 
    "term": clinton, 
    "trend": True | False,
    "summary": {time : summarized text }, 
    "future trending spike times": []
}

The summary is the spikes and a summarization of the tweets at the spikes.



### Obtain a list of alerts

Parameters: N/A

method: /v1/listing

Usage:

```
$ curl -u miguel:python -i -X GET http://127.0.0.1:8001/v1/listing
```

Output: list of triggers term in the system


### Delete alert


Parameters: N/A

method: /v1/delete/alert

Usage:

```
$ curl -u miguel:python -i -X POST -H "Content-Type: application/json" -d '{"term":"clinton"}' http://127.0.0.1:8001/v1/delete/alert

```

Output: list of alerts in the system



# Summary of API 

Version: v1

POST /v1/api/users
Create a new users.

GET /v1/alerts/`<term>`
Obtain data stream.

GET /v1/alerts/`<term>/<aggregation>`
Obtain data stream.

POST /v1/alerts
Obtain a batch of data stream.

GET /v1/listing
Obtain a list of triggers in the system.

POST /v1/delete/alert
Delete the trigger.


# Error messages
The default errorcode is 400. This is usually thrown when there is missing arguments.

Other HTTP code 401 is thrown for bad authentication.

