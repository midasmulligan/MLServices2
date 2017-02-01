from __future__ import division
from datetime import datetime, timedelta, date
import os, random, string
import calendar


def totimestamp(dt, epoch=datetime(1970,1,1)):
    td = dt - epoch
    # return td.total_seconds()
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6 


def timestampinUTC ():
    #this returns the time in UTC
    now = datetime.utcnow()
    return int (totimestamp(now))


def convertDateStringToUTCtimestamp (date_string):
    """
        date_string = "01/12/2011"
    """
    date_object = date(*map(int, reversed(date_string.split("/"))))
    timestamp = calendar.timegm(date_object.timetuple())
    return timestamp 


def getCurrentKey (curUnixTimestamp=timestampinUTC (), aggreg=3600):
    '''
        input:
            curUnixTimestamp is current time in seconds.
            aggreg is in seconds e.g 5 minutes, 30 minutes, 1 hour
    '''
    nearestTimeStampInAgg = int (curUnixTimestamp / aggreg ) * aggreg #round to nearest aggreg 
    lastTimeStampInAgg = nearestTimeStampInAgg - aggreg # go back one aggreg value
    key = str ( lastTimeStampInAgg ) +"-" + str ( nearestTimeStampInAgg ) 
    #key = "1476843914-1476847514"  
    #key = "kenneth"
    return key



def getPassword (length = 60):
    """
        password of length specified
    """
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))

    return ''.join(random.choice(chars) for i in range(length))
