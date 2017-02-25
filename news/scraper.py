import requests
import lxml
from lxml import html
import json


apiKey="b5cb4418725248dab9b0874911ebb69e"
sourceURL = "https://newsapi.org/v1/sources"
articleURL = "https://newsapi.org/v1/articles"




def getNews (language = "en", apiKey=apiKey, category = None ):
    """
        category can be business, entertainment, gaming, general, music, science-and-nature, sport, technology

        language can be en, de, fr
    """
    output = []
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
            output.append ( articleObj["description"] ) 

    return output


if __name__ == '__main__':

    categoryList = ["business", "entertainment", "gaming", "general", "music", "science-and-nature", "sport", "technology"]
    for cat in categoryList:
        print cat + " : " + str ( len (getNews ( category = cat )) )


