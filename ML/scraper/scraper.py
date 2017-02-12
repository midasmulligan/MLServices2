import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

import requests as req
import lxml
from lxml import html

import json
import re

import pandas as pd
import numpy as np


import re 



from bs4 import BeautifulSoup
from cStringIO import StringIO

from lxml.html.clean import Cleaner


cleaner = Cleaner()
cleaner.javascript = True # This is True because we want to activate the javascript filter
cleaner.style = True      # This is True because we want to activate the styles & stylesheet filter


blacklist = ['http://www.cnbc.com/sign-up-for-cnbc-newsletters/', 'http://www.nbcuniversal.com/privacy/', 'http://www.cnbc.com/id/16061983', 'http://www.cnbc.com', 'javascript:void(0),', None, 'www.cnbc.com/markets/', '/nbcuni.com/privacy/']


_digits = re.compile('\d')
def contains_digits(d):
    return bool(_digits.search(d))


class BBCFilter ():
    def readCurrentURL(self, url):
        r = req.get(url, timeout=None)
        soup = BeautifulSoup(r.content, 'html.parser')

        buf = StringIO()
        for ptag in soup.find_all('p'):
            if ptag.get('class') is None or ptag.get('class')== "story-body__introduction":
                buf.write( ptag.get_text().lower() + " "  )
        return buf.getvalue()


    def getListOfURL (self, query):
        #brexit, us+fed
        payload = {'q': query, 'sa_f': 'search-product', 'scope': '#page=1'}
        r = req.get("http://www.bbc.co.uk/search", params=payload, timeout=None)

        tree = lxml.html.fromstring( r.content )
        atags = tree.findall('.//h1/a') #get informative text

        list_of_urls = [ el.get('href') for el in atags] 
        return list_of_urls


    #url = 'http://www.bbc.com/news/election/us2016'
    def getListOfURLFromAggregatedPage (self, url):
        #US Elections
        r = req.get(url, timeout=None)
        tree = lxml.html.fromstring( r.content )

        scripttags = tree.findall('.//script') #get informative text
        json_string = scripttags[1].text_content()
        dictObj = json.loads(json_string)
        list_of_urls = [ obj['url'] for obj in dictObj['itemListElement'] ]
        return list_of_urls


    def readAllURLFromQuery (self, query):
        totallist = []
        urllist = self.getListOfURL (query)
        for url in urllist:
            if contains_digits(url):
                totallist.append (url)
            else:
                listOfURL = self.getListOfURLFromAggregatedPage (url)
                for innerurl in listOfURL:
                    if innerurl not in totallist: #avoid duplicate
                        totallist.append (innerurl)

        return totallist


    def getAllURLContent (self, query):
        buf = StringIO()
        listOfURL = self.readAllURLFromQuery (query)
        for url in listOfURL:
            content = self.readCurrentURL(url)
            buf.write( content + " "  )
        return buf.getvalue()


    def getContentFromAggregatedURL (self, url):
        listOfURL = self.getListOfURLFromAggregatedPage (url)

        buf = StringIO()
        for curl in listOfURL:
            content = self.readCurrentURL(curl)
            buf.write( content + " " )
        return buf.getvalue()


#http://www.cnbc.com/brexit/
#http://www.cnbc.com/elections/
#http://www.cnbc.com/federal-reserve/





class CNBCFilter ():
    base_url = 'http://www.cnbc.com'
    def readCurrentURL(self, url):
        r = req.get(self.base_url+url, timeout=None)
        buf = StringIO()

        tree = lxml.html.fromstring( cleaner.clean_html(r.content) )
        content = tree.findall(".//div[@class='group']") #get informative text
        for ind in range ( len (content) ):
            buf.write( content[ind].text_content().lower() + " "  )
        return buf.getvalue()


    def getListOfURL (self, query):
        #query can be brexit, elections, federal-reserve
        r = req.get(self.base_url + "/" + query + "/", timeout=None)

        tree = lxml.html.fromstring( cleaner.clean_html(r.content) )
        atags = tree.findall('.//div/a') #get informative text

        list_of_urls = [ el.get('href') for el in atags if el.get('href') not in blacklist] 
        return list_of_urls


    def getAllURLContent (self, query):
        buf = StringIO()
        listOfURL = self.getListOfURL (query)
        for url in listOfURL:
            if url.find ("video") == -1 and url.find ("markets") == -1 and url.find ("privacy") == -1:
                content = self.readCurrentURL(url)
                buf.write( content + " "  )
        return buf.getvalue()





#http://www.independent.co.uk/topic/us-election-2016
#http://www.independent.co.uk/topic/brexit
#http://www.independent.co.uk/topic/Economics


class IndependentFilter ():
    base_url = 'http://www.independent.co.uk'
    def readCurrentURL(self, url):
        r = req.get(self.base_url+url, timeout=None)
        buf = StringIO()

        tree = lxml.html.fromstring( cleaner.clean_html(r.content) )
        content = tree.findall(".//div[@class='text-wrapper']") #get informative text
        for ind in range ( len (content) ):
            buf.write( content[ind].text_content().lower() + " "  )
        return buf.getvalue()



    def getListOfURL (self, query):
        #query can be brexit, us-election-2016, Economics
        url = 'http://www.independent.co.uk/topic'
        r = req.get(url + "/" + query, timeout=None )

        tree = lxml.html.fromstring( cleaner.clean_html(r.content) )
        atags = tree.findall('.//h1/a') #get informative text

        list_of_urls = [ el.get('href') for el in atags] 

        return list_of_urls



    def getAllURLContent (self, query):
        buf = StringIO()
        listOfURL = self.getListOfURL (query)
        for url in listOfURL:
            content = self.readCurrentURL(url)
            buf.write( content + " "  )
        return buf.getvalue()



class France24Filter ():
    #base_url = 'http://www.france24.com/en/france/'

    def readCurrentURL(self, url):
        r = req.get(url, timeout=None)
        buf = StringIO()

        tree = lxml.html.fromstring( cleaner.clean_html(r.content) )
        content = tree.findall(".//div[@class='bd']/") #get informative text

        for ind in range ( len (content) ):
            buf.write( content[ind].text_content().lower() + " "  )
        return buf.getvalue()



    def getListOfURL (self, query):
        #query france
        url = "http://www.france24.com/en/"
        r = req.get(url + "/" + query, timeout=None )

        tree = lxml.html.fromstring( cleaner.clean_html(r.content) )
        atags = tree.findall(".//p[@class='default-read-more']/a") #get informative text

        innerBaseURL = "http://www.france24.com"

        list_of_urls = [ innerBaseURL+el.get('href') for el in atags ] 

        return list_of_urls



    def getAllURLContent (self, query):
        buf = StringIO()
        listOfURL = self.getListOfURL (query)
        for url in listOfURL:
            content = self.readCurrentURL(url)
            buf.write( content + " "  )
        return buf.getvalue()



class WikipediaFilter ():
    def getContentURL (self,url):
        r = req.get(url, timeout=None)
        tree = lxml.html.fromstring(r.content)

        buf = StringIO()
        for el in tree.findall('.//div/p'):
            buf.write( re.sub("[\[].*?[\]]", "", el.text_content()) + " " )
        return buf.getvalue()




class CompositeFilter():
    indObj = IndependentFilter ()
    cnbcObj = CNBCFilter ()
    bbcObj = BBCFilter ()

    france24Obj = France24Filter ()

    wikiObj= WikipediaFilter ()


    def getBrexitData (self):
        buf = StringIO()
        query = "brexit"

        content = self.indObj.getAllURLContent (query)
        buf.write( content + " "  )

        content = self.cnbcObj.getAllURLContent (query)
        buf.write( content + " "  )

        content = self.bbcObj.getAllURLContent (query)
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/Brexit"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        return buf.getvalue()


    def getUSFedData (self):
        buf = StringIO()
        content = self.indObj.getAllURLContent ("Economics")
        buf.write( content + " "  )

        content = self.cnbcObj.getAllURLContent ("federal-reserve")
        buf.write( content + " "  )

        content = self.bbcObj.getAllURLContent ("us+fed")
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/Federal_Reserve_System"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        return buf.getvalue()


    def getUSElectionData (self):
        buf = StringIO()
        content = self.indObj.getAllURLContent ("us-election-2016")
        buf.write( content + " "  )

        content = self.cnbcObj.getAllURLContent ("elections")
        buf.write( content + " "  )

        url = 'http://www.bbc.com/news/election/us2016'
        content = self.bbcObj.getContentFromAggregatedURL (url)
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/United_States_presidential_election,_2016"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        return buf.getvalue()


    def getFrenchPoliticsData (self):
        buf = StringIO()

        content = self.bbcObj.getAllURLContent ("french+politics")
        buf.write( content + " "  )

        content = self.france24Obj.getAllURLContent ("france")
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/Politics_of_France"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/List_of_political_parties_in_France"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/Government_of_France"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/French_presidential_election,_2017"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        return buf.getvalue()


    def getTrumpData (self):
        buf = StringIO()

        content = self.bbcObj.getAllURLContent ("trump")
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/Donald_Trump"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        return buf.getvalue()



    def getLePenData (self):
        buf = StringIO()

        url = "https://en.wikipedia.org/wiki/Marine_Le_Pen"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/Jean-Marie_Le_Pen"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        return buf.getvalue()



    def getIranNuclearData (self):
        buf = StringIO()

        url = "https://en.wikipedia.org/wiki/Joint_Comprehensive_Plan_of_Action"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/Joint_Plan_of_Action"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/P5%2B1"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/Sanctions_against_Iran"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )


        url = "https://en.wikipedia.org/wiki/Nuclear_program_of_Iran"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/Iran_nuclear_deal_framework"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        return buf.getvalue()


    def getIranElectionData (self):
        buf = StringIO()

        url = "https://en.wikipedia.org/wiki/Iranian_legislative_election,_2016"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        url = "https://en.wikipedia.org/wiki/Iranian_presidential_election,_2017"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        return buf.getvalue()


    def getShinzoAbeData (self):
        buf = StringIO()

        url = "https://en.wikipedia.org/wiki/Shinz%C5%8D_Abe"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        return buf.getvalue()


    def getTheresaMayData (self):
        buf = StringIO()

        url = "https://en.wikipedia.org/wiki/Theresa_May"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        return buf.getvalue()


    def getAngelaMerkelData (self):
        buf = StringIO()

        url = "https://en.wikipedia.org/wiki/Angela_Merkel"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        return buf.getvalue()


    def getGermanElectionData (self):
        buf = StringIO()

        url = "https://en.wikipedia.org/wiki/German_federal_election,_2017"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        return buf.getvalue()


    def getRecepTayyipData (self):
        buf = StringIO()

        url = "https://en.wikipedia.org/wiki/Recep_Tayyip_Erdo%C4%9Fan"
        content = self.wikiObj.getContentURL (url)
        buf.write( content + " "  )

        return buf.getvalue()





    def getTotalData (self):
        cols = tuple(['label', 'message'])
        df = pd.DataFrame(columns=cols)

        brexitData = self.getBrexitData ()
        fedData = self.getUSFedData ()
        electData = self.getUSElectionData ()

        frenchPoliticsData = self.getFrenchPoliticsData ()
        trumpData = self.getTrumpData ()

        lePenData = self.getLePenData ()

        iranNuclearData = self.getIranNuclearData ()

        iranElectionData = self.getIranElectionData ()

        shinzoAbeData = self.getShinzoAbeData ()

        theresaMayData = self.getTheresaMayData ()

        angelaMerkelData = self.getAngelaMerkelData ()

        germanElectionData = self.getGermanElectionData ()

        recepTayyipData = self.getRecepTayyipData ()

        labels = ["Brexit", "US federal Reserve", "Us Election", "French Politics", "Trump", "Le Pen", "Iran Nuclear Deal", "Iran Election", "Shinzo Abe", "Theresa May", "Angela Merkel", "German Election", "Erdogan"]

        dataList = [brexitData, fedData, electData, frenchPoliticsData, trumpData, lePenData, iranNuclearData, iranElectionData, shinzoAbeData, theresaMayData, angelaMerkelData, germanElectionData, recepTayyipData]

        for i in range(len (labels)):
            df.loc[i] = [labels[i], dataList[i]]

        df.to_csv("topicCollection.csv", header=True)



if __name__ == "__main__":
    '''
    indObj = IndependentFilter ()
    print indObj.getAllURLContent ("brexit")
    print indObj.getAllURLContent ("us-election-2016")
    print indObj.getAllURLContent ("Economics")

    cnbcObj = CNBCFilter ()
    print cnbcObj.getAllURLContent ("brexit")
    print cnbcObj.getAllURLContent ("elections")
    print cnbcObj.getAllURLContent ("federal-reserve")
        
    bbcObj = BBCFilter ()
    print bbcObj.getAllURLContent ("brexit")
    print bbcObj.getAllURLContent ("us+fed")
    url = 'http://www.bbc.com/news/election/us2016'
    print bbcObj.getContentFromAggregatedURL (url)
    '''
    compObj = CompositeFilter()
    compObj.getTotalData ()


