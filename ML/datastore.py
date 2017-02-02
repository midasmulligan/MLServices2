import psycopg2
from pandas import read_sql
import json
from cStringIO import StringIO
import time

config = { 'dbname': 'newsdb', 
           'user': 'test',
           'pwd': 'test',
           'host': 'localhost',
           'port':'5432'
}


class DataStore ():


    def __init__( self ):
        '''
            Constructor
        '''
        self.conn = self.create_conn(config=config)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()


    def create_conn(*args,**kwargs):
        config = kwargs['config']
        try:
            con=psycopg2.connect(dbname=config['dbname'], host=config['host'], port=config['port'], user=config['user'], password=config['pwd'])
            
            return con
        except Exception as err:
            print(err)


    def createTable( self, term ):
        '''
            create new table
        '''

        #query = "CREATE TYPE sentimentValue AS ENUM ('pos', 'neg', 'neu'); CREATE TABLE IF NOT EXISTS "+ term + " ( tweetid bigint NOT NULL PRIMARY KEY, text varchar(500) NOT NULL, timestamp bigint NOT NULL, sentiment sentimentValue  );"

        query = " CREATE TABLE IF NOT EXISTS "+ term + " ( tweetid bigint NOT NULL, text varchar(500) NOT NULL, timestamp bigint NOT NULL, sentiment varchar(3)  );"

        self.cur.execute(query)

        # Make the changes to the database persistent
        self.conn.commit()

        print "Table :" + term +" is created!!!"


    def removeTable( self, term ):
        '''
            remove new table
        '''
        #query = " DROP TABLE "+ term + ";"

        query ="DROP TABLE IF EXISTS " + term + " CASCADE;"

        self.cur.execute(query)

        # Make the changes to the database persistent
        self.conn.commit()

        print "Table :" + term +" is deleted!!!"



    def addRowToTable( self, term, tweetid, text, timestamp, sentiment=None ):
        '''
            add row to table
        '''
        if sentiment is None:
            self.cur.execute("INSERT INTO "+term+" (tweetid, text, timestamp) VALUES (%s,%s,%s)",  ( tweetid, text, timestamp) )

        else:
            self.cur.execute("INSERT INTO "+term+" (tweetid, text, timestamp, sentiment) VALUES (%s,%s,%s,%s)",  ( tweetid, text, timestamp, sentiment) )

        #print "New row added in the Table :" + term 


    def getEveryRow( self, term ):
        '''
            add row to table
        '''
        output = []
        query="SELECT * from "+ term  + ";"
        self.cur.execute(query)
        row = self.cur.fetchone()
        while row:
            output.append (row)
            row = self.cur.fetchone()

        return output


    def getDF( self, term, start_timestamp, end_timestamp, sentiment = None ):
        '''
            get dataframe
        '''
        query = ""
        if sentiment is None:
            query = "select text, timestamp from "+ term + " where timestamp between " + str(start_timestamp) + " and " + str(end_timestamp)

        else:
            query = "select text, timestamp from "+ term + " where sentiment=" + str(sentiment)+" AND timestamp between " + str(start_timestamp) + " and " + str(end_timestamp)

        df = read_sql(query, con=self.conn) 
        return df


    def table_exists( self, table_str ):
        exists = False
        try:
            query = "select exists(select relname from pg_class where relname='" + table_str + "')"
            self.cur.execute(query)
            exists = self.cur.fetchone()[0]
            #self.cur.close()
        except psycopg2.Error as e:
            print e
        return exists



    def __del__(self):
        # Close communication with the database
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    dsObj = DataStore ()


    #term = "kenneth"
    term = "james"
    dsObj.removeTable( term )
    
    
    dsObj.createTable( term )


    dsObj.addRowToTable( term, 177384834569, "Please am coming home", 45332228, 'pos' )
    dsObj.addRowToTable( term, 177384838297, "Please am seeing him", 45332229916, 'neg' )
    print dsObj.getEveryRow( term )
    print "======================================="
    print "======================================="
    print "=======================================\n"
    print dsObj.getDF(  term, 1000, 100000000 )


    print dsObj.table_exists( "james")

    print dsObj.table_exists( "kenneth")


