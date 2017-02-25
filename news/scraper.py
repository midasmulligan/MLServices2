import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
import pandas as pd

import requests
import lxml
from lxml import html
import json

from cStringIO import StringIO


apiKey     = "b5cb4418725248dab9b0874911ebb69e"
sourceURL  = "https://newsapi.org/v1/sources"
articleURL = "https://newsapi.org/v1/articles"




def getNews (language = "en", apiKey=apiKey, category = None ):
    """
        category can be business, entertainment, gaming, general, music, science-and-nature, sport, technology

        language can be en, de, fr
    """
    buf = StringIO()
    payload = {'language': language, 'apiKey': apiKey}

    if category:
        payload = {'language': language, 'apiKey': apiKey, 'category' : category}

    req = requests.get( sourceURL, params=payload )

    downloadObj = json.loads( req.content ) 

    sourceObjList = downloadObj["sources"]

    for sourceObj in sourceObjList:
        payload = {'source': sourceObj["id"], 'apiKey': apiKey}
        req = requests.get( articleURL, params=payload )

        downloadContentObjlist = json.loads( req.content ) 

        articleObjList = downloadContentObjlist["articles"]

        for articleObj in articleObjList:
            buf.write( str(articleObj["description"]).lower() + " " )

    return buf.getvalue()


def getLabeledData ():

    cols = tuple(['label', 'message'])
    df = pd.DataFrame(columns=cols)

    dataList = []
    labels  = ["business", "entertainment", "gaming", "general", "music", "science-and-nature", "sport", "technology"]
  


    for i in range(len (labels)):
        df.loc[i] = [labels[i], getNews ( category = labels[i] )]

    df.to_csv("topicCollection.csv", header=True, index=False)


if __name__ == '__main__':
    getLabeledData ()

